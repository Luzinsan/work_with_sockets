#include <iostream>
#include "Socket.h"
#define DOMAIN AF_INET
#define TYPE SOCK_STREAM
#define PROTOCOL IPPROTO_TCP
#define PORT 50354


int main()
{
    Socket server(PORT);
    try
    {
        server.cycle();
    }
    catch(std::exception err)
    {
        server.~Socket();
    };
    return 0;
}