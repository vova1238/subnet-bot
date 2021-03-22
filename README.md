[Українською](./README_ukr.md)

# subnet-bot
subnet-bot - a telegram chatbot that should help system and network administrators reduce routine computing when designing, optimizing, or reorganizing computer networks.

The main function of the chatbot is to count the required number of subnets for the IP address based on the number of hosts required by the user or vice versa - the number of hosts by the number of subnets.

### Also in chatbot implemented these functions:
1. Getting information about IP addresses
2. Obtaining the location of the IP address on the map
3. Summation of ip-addresses in the supernetwork

The project is written in Python version 3.8.7, uses the pyTelegramBotAPI library version 3.7.6, also borrowed several functions from the project [thimoonxy/subnetting](https://github.com/thimoonxy/subnetting)