# імпортування модулю для роботи з регулярними виразами
import re

# Функція перевірки адреси
def is_valid_ip(input_str):
    return re.match(r'^((25[0-5]|(2[0-4]|1[0-9]|[1-9]|)[0-9])(\.(?!$)|$)){4}$', input_str)

# Функція перевірки маски мережі
def is_valid_mask(input_str):
    return re.match(r'^((128|192|224|240|248|252|254)\.0\.0\.0)|(255\.(((0|128|192|224|240|248|252|254)\.0\.0)|(255\.(((0|128|192|224|240|248|252|254)\.0)|255\.(0|128|192|224|240|248|252|254)))))$', input_str)

# Функція перетворення префіксів маски у маску
def cidr2mask(cidr='24'):
    cidr=int(cidr)
    fullnet = '0b11111111'
    zeronet = '0b00000000'
    if cidr <= 8:
        hosts = 8 - cidr
        net = '0b' + '1'* cidr + '0' * hosts
        net = (net, zeronet, zeronet, zeronet)
    elif 8 < cidr <= 16:
        hosts = 16 - cidr
        net = '0b' + '1'* (cidr-8) + '0' * hosts
        net = (fullnet, net, zeronet, zeronet)
    elif 16 < cidr <= 24:
        cidr = cidr - 16
        hosts = 8 - cidr
        net = '0b' + '1'* cidr + '0' * hosts
        net = (fullnet, fullnet, net, zeronet)
    else:
        cidr = cidr - 24
        hosts = 8 - cidr
        # print cidr,hosts
        net = '0b' + '1'* cidr + '0' * hosts
        net = (fullnet, fullnet, fullnet, net)
    netmask = '.'.join([ str(int(net[x], 2)) for x in range(len(net)) ])
    return netmask

# Функція перетворення маски у префікс маски
def mask2cidr(mask='255.255.255.0'):
    '''
    1.  '255.11111.266.4' to '255.255.255.0' to 24
    2.  '255.128.255.0'  to 9
    '''
    mask_list = mask.split('.')
    mask_list = map(int,mask_list)                         # Список цілих чисел
    notexcess = lambda x: ( x > 255) and 255 or x          # Якщо якась більше за 255, то виставити 255
    addzero= lambda x : ( x not in "10" ) and '0' or x
    mask_list = map(notexcess, mask_list)
    binmask_total=''
    for x in mask_list:
    #for x in range(4):
        binmask = "%8s" %bin(x).split('0b')[1]              #  '    1101'
        binmask = ''.join(map(addzero,list(binmask)))       #  '00001101'  , addzero
        binmask_total += binmask
    try:
        zindex = binmask_total.index('0')
    except ValueError:
        zindex = 32
    return  zindex

# Функція перетворення ip у список бітів
def ip2binlist(ip):
    addzero= lambda x : ( x not in "10" ) and '0' or x
    iplist = ip.split('.')
    iplist = map(int,iplist)
    binlist = []
    for x in iplist:
        binmask = "%8s" %bin(x).split('0b')[1]              #  '    1101'
        binmask = ''.join(map(addzero,list(binmask)))       #  '00001101'  , addzero
        binlist.append(binmask)
    return binlist

# Функція перетворення маски в укомплектований список бітів
def mask2complement_bin_list(mask='255.255.255.0'):
    xcomplement_bin_list = ip2binlist(mask)
    anti = lambda x: (x == '1') and '0' or '1'
    complement_bin_list = [  ''.join(map(anti,list(x))) for x in xcomplement_bin_list ]
    return  complement_bin_list

# Функція перетворення ip у адресу марежі
def ip2network_address(ip='192.168.1.0', cidr='32'):
    """
    This func also corrects wrong subnet, e.g.
    if found 10.69.231.70/29, it'll be corrected to 10.69.231.64/29.
    """
    ip = ip.split('.')
    netmask = cidr2mask(cidr)
    bin_mask_list = ip2binlist(netmask)
    for x in range(len(ip)):
        ip[x] = int(ip[x]) & int(bin_mask_list[x], 2)
    if int(cidr) < 31:
        network_address = "%s.%s.%s.%s" % (ip[0], ip[1], ip[2], ip[3])
        first_avail_ip = "%s.%s.%s.%s" % (ip[0], ip[1], ip[2], ip[3]+1)
        avail_host_numbers = 2 ** (32 - int(cidr)) - 2
        complement_bin_list = mask2complement_bin_list(netmask)
        broadcast_address = '.'.join([ str(ip[x]+int(complement_bin_list[x],2)) for x in range(4)])
        last_avail_ip_list = broadcast_address.split('.')[0:3]
        last_avail_ip_list.append( str( int(broadcast_address.split('.')[-1]) -1 ) )
        last_avail_ip = '.'.join(last_avail_ip_list)
    elif int(cidr) == 31:
        broadcast_address = network_address = None
        first_avail_ip = "%s.%s.%s.%s" % (ip[0], ip[1], ip[2], ip[3])
        last_avail_ip = "%s.%s.%s.%s" % (ip[0], ip[1], ip[2], ip[3]+1)
        avail_host_numbers = 2
    else:
        broadcast_address = network_address = None
        first_avail_ip = "%s.%s.%s.%s" % (ip[0], ip[1], ip[2], ip[3])
        last_avail_ip = first_avail_ip
        avail_host_numbers = 1
    return  avail_host_numbers, netmask, network_address, first_avail_ip,last_avail_ip, broadcast_address

# Функція отримання класу ip
def ip2class(ip):
    '''
    A: Leading bits  0
    B: Leading bits  10
    C: Leading bits  110
    D: Leading bits  1110   (multicast)
    E: Leading bits  1111   (reserved)

    References:
    1. https://en.wikipedia.org/wiki/Classful_network#Introduction_of_address_classes
    2. http://www.tcpipguide.com/free/t_IPAddressClassABandCNetworkandHostCapacities.htm

    In the following table:
       - n indicates a bit used for the network ID.
       - H indicates a bit used for the host ID.
       - X indicates a bit without a specified purpose.

    Class A
    0.  0.  0.  0   =   00000000.00000000.00000000.00000000
    127.255.255.255 =   01111111.11111111.11111111.11111111
                        0nnnnnnn.HHHHHHHH.HHHHHHHH.HHHHHHHH
    Class B
    128.  0.  0.  0 =   10000000.00000000.00000000.00000000
    191.255.255.255 =   10111111.11111111.11111111.11111111
                        10nnnnnn.nnnnnnnn.HHHHHHHH.HHHHHHHH
    Class C
    192.  0.  0.  0 =   11000000.00000000.00000000.00000000
    223.255.255.255 =   11011111.11111111.11111111.11111111
                        110nnnnn.nnnnnnnn.nnnnnnnn.HHHHHHHH
    Class D
    224.  0.  0.  0 =   11100000.00000000.00000000.00000000
    239.255.255.255 =   11101111.11111111.11111111.11111111
                        1110XXXX.XXXXXXXX.XXXXXXXX.XXXXXXXX
    Class E
    240.  0.  0.  0 =   11110000.00000000.00000000.00000000
    255.255.255.255 =   11111111.11111111.11111111.11111111
                        1111XXXX.XXXXXXXX.XXXXXXXX.XXXXXXXX
    '''

    classful_dict = {
        int('1' * 1 + '0' * (8 - 1), 2): 'B',
        int('1' * 2 + '0' * (8 - 2), 2): 'C',
        int('1' * 3 + '0' * (8 - 3), 2): 'D',
        int('1' * 4 + '0' * (8 - 4), 2): 'E',
    }
    ip = ip2binlist(ip)[0]  # ip,  <type 'str'>
    if int(ip,2) > 255:     # typo, should be 0 <= ip <= 255
        return None
    flags=[]
    for leading in classful_dict.keys():
        if (int(ip,2) & leading) == leading:
            flags.append(leading)
    if len(flags) == 0:
        return 'A'
    return classful_dict[max(flags)]

# Функція перетворення кількості хостів у cidr
def hostamount2cidr(amount=1):
    constant_hostnumber_list = []
    for cidr in range(32,-1,-1):
        constant_hostnumber_list.append( ip2network_address(cidr=cidr)[0])
        if ip2network_address(cidr=cidr)[0] >= amount:
            return cidr

# Функція перетворення строки бітів у список бітів
def bin2binlist(binstr):
    raw_list = []
    result_list = []
    for x in list(binstr):
        if len(raw_list) != 7:
            raw_list.append(x)
        else:
            raw_list.append(x)
            result_list.append(''.join(raw_list))
            raw_list = []
    return  result_list

# Функція перетворення списку бітів у ip
def binlist2ip(binlist):
    add_bin_prefix = lambda binstr: '0b' + binstr
    bin2int = lambda bstr: str( int(bstr,2))
    binlist = map(add_bin_prefix,binlist)
    ip = '.'.join( map(bin2int,binlist)  )
    return ip

# Функція знаходження підмереж 
def subnetting(ip='192.168.0.1', host_amount=None, subnet_amount=None):
    """
    Returns: 
    cidr, class, flag, len(network_address_list), network_address_list, avail_host_amount
    """
    default_netbits_dict = {
        'A' : 8,
        'B' : 16,
        'C' : 24,
    }

    c = ip2class(ip)
    if c not in default_netbits_dict.keys():
        raise ValueError("\nWarning, Class %s not allowed subnetting.\n" %c)
    default_cidr = default_netbits_dict[c]
    default_network_address = ip2network_address(ip,default_cidr)[2]
    default_network_address_bin_list = ip2binlist(default_network_address)
    default_network_address_bin_str = ''.join(default_network_address_bin_list)
    
    int2binlist = lambda i:  [ bin(x).split('0b')[1].zfill(i)   for x in range(2 ** i)   ]
    '''
    In [121]: int2binlist(2)
    Out[121]: ['00', '01', '10', '11']

    In [122]: int2binlist(3)
    Out[122]: ['000', '001', '010', '011', '100', '101', '110', '111']
    '''

    if host_amount:
        host_amount = int(host_amount)
        network_address_list = []
        cidr = hostamount2cidr(host_amount)
        subnet_bits = cidr - default_cidr
        avail_host_amount = ip2network_address(ip,cidr)[0]
        if subnet_bits > 0:
            flag = 'subnet'
            subnet_amount = 2 ** subnet_bits
            sub_binlist = int2binlist(subnet_bits)
            
            for subbinstr in sub_binlist:
                fullbinstr = ''.join([ list(default_network_address_bin_str)[x] for x in range(default_cidr)]) + subbinstr + '0' * (32 - cidr)
                
                binlist = bin2binlist(fullbinstr)
                
                network_address_list.append( binlist2ip(binlist)  )
        else:
            flag = 'supernet'
            subnet_amount = 1
            network_address = ip2network_address(ip,cidr)[2]
            network_address_list.append(network_address)
        return cidr, c, flag, subnet_amount,network_address_list, avail_host_amount

    elif subnet_amount:
        subnet_amount = int(subnet_amount)
        network_address_list = []
        subnet_bits = min( [ subnet_bits for subnet_bits in range(32) if 2 ** subnet_bits >= subnet_amount ] )
        cidr = subnet_bits + default_cidr
        avail_host_amount = ip2network_address(ip,cidr)[0]
        if subnet_bits > 0:
            flag = 'subnet'
            sub_binlist = int2binlist(subnet_bits)
            for subbinstr in sub_binlist:
                fullbinstr = ''.join([ list(default_network_address_bin_str)[x] for x in range(default_cidr)]) + subbinstr + '0' * (32 - cidr)
                
                binlist = bin2binlist(fullbinstr)
                
                network_address_list.append( binlist2ip(binlist)  )
        else:
            flag = 'supernet'
            subnet_amount = 1
            network_address = ip2network_address(ip,cidr)[2]
            network_address_list.append(network_address)
        return cidr, c, flag, len(network_address_list), network_address_list, avail_host_amount

# Функція перетворення строки з ip адрес у список адрес
def ip_str2list(addr_str):
    addr_str = addr_str.rstrip(',')
    addr_list = addr_str.split(sep=',')
    addr_list = list(map(lambda x: str.replace(x, '\n', '').replace(' ', ''), addr_list))
    valid_ip_list = []
    invalid_ip_list = []
    for addr in addr_list:
        ip, cidr = addr.split(sep='/')
        if is_valid_ip(ip) and 0 < int(cidr) < 33:
            valid_ip_list.append(addr)
        else:
            invalid_ip_list.append(addr)
    return valid_ip_list, invalid_ip_list

# Функція сумування ip-адрес
def summation(ip_list):
    binlist = [''.join(ip2binlist(inp.split('/')[0])) for inp in ip_list]
    min_cidr = min([int(''.join(inpcidr.split('/')[1])) for inpcidr in ip_list])
    result = []
    for i in range(1, len(binlist)):
        pointer = 0
        for ch1, ch2 in zip(binlist[i-1], binlist[i]):
            if ch1 == ch2:
                pointer+=1
            else:
                break
        result.append(pointer)
    cidr = min(min(result), min_cidr)
    bin_ip = binlist[0][:cidr] + '0' * (32 - cidr)
    sep_bin_ip = [bin_ip[:8],bin_ip[8:16],bin_ip[16:24],bin_ip[24:]]
    ip = binlist2ip(sep_bin_ip)
    net_info = ip2network_address(ip,cidr)
    return cidr, bin_ip , *net_info
