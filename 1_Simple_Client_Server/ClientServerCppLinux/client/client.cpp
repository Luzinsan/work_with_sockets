#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <unistd.h>
#include <iostream>
#define PORT 50335
#define NUM_ADDR 6
#define LEN_STR 16

int sendall(int sockfd, const char* buf, size_t len, int flags);
int recvall(int sockfd, char *buf, size_t len, int flags);
int recvall(int sockfd, char** buf, size_t h_count=NUM_ADDR, size_t len=LEN_STR, int flags=0);

int main()
{
    int sock;
    struct sockaddr_in addr;

    sock = socket(AF_INET, SOCK_STREAM, 0);
    if(sock < 0)
    {
        perror("socket");
        exit(1);
    }
    
    addr.sin_family = AF_INET;
    addr.sin_port = htons(PORT); // или любой другой порт...
    //addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    inet_pton(PF_INET, "127.0.0.4", &addr.sin_addr.s_addr);
    if(connect(sock, reinterpret_cast<const struct sockaddr *>(&addr), sizeof(addr)) < 0)
    {
        perror("connect");
        exit(2);
    }
    else
        std::cout << "Client socket: " << sock 
                    << "\nsocked address: " << inet_ntoa(addr.sin_addr) 
                    << "\nsocket port: " << ntohs(addr.sin_port);


    
    char host[1024] = "google.com";
    std::cout << "\nName of host: ";
    std::cout << host << "\n";
    //std::cin >> host;
    char** name_host = new char*[4];

    sendall(sock, host, 1024, 0);
    recvall(sock, name_host);
    for(int i = NUM_ADDR-1; i > 0; i--)
    {
        printf("%s",  name_host[i]);
        std::cout << std::endl;
        //std::cout << name_host[i] << "\n";
        delete[] name_host[i];
    }
    printf("%s",  *name_host);
    std::cout << std::endl;
    delete[] name_host;
    

    close(sock);

    return 0;
}


int sendall(int sockfd, const char* buf, size_t len, int flags)
{
    int total = 0;
    int n;
    while(total < len)
    {
        n = send(sockfd, buf+total, len - total, flags);
        if(n == -1) { break;}
        total += n;
    }
    return (n == -1 ? -1 : total);
}

int recvall(int sockfd, char** buf, size_t h_count, size_t len, int flags)
{
    int succ = h_count;
    for(int i = 0; i < h_count; i++)
    { 
        buf[i] = new char[len];
        if(recvall(sockfd,  buf[i], len, flags) == -1)
            succ -= 1;
    }
    return succ;
}

int recvall(int sockfd, char *buf, size_t len, int flags)
{
    int total = 0;
    int n;
    while(total < len)
    {
        n = recv(sockfd, buf + total, len - total, flags);
        //std::cout << buf;
        if(n == -1 || n == 0) { break; }
        total += n;
    }
    return (n == -1 ? -1 : total);
}