#include <iostream>
// linux
#include <sys/types.h> 
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <unistd.h>
#include <string.h>

typedef int FDESCRIPTOR;

#define LISTENQ SIZE_MAX
#define ERROR    -1
#define SOCK_FAIL 1
#define BIND_FAIL 2
#define LISTEN_FAIL 2
#define ACCEPT_FAIL 3
#define SEND_FAIL 4


class Socket
{
private:
    FDESCRIPTOR server_sock, client_sock;
    int domain;
    int type;
    int protocol;
    unsigned short port;
    in_addr_t ip;
    struct sockaddr_in sin, clin;
    socklen_t len_ssock, len_clsock;
public:

    Socket(unsigned short __port, char* __ip="127.0.0.4",
           int __domain=AF_INET, int __type=SOCK_STREAM, int __protocol=IPPROTO_TCP)
          :Socket(__domain, __type, __protocol)
    {
        sin.sin_family = domain;
        ip = inet_addr(__ip);
        //inet_pton(__domain, __ip, &ip);
        sin.sin_addr.s_addr = ip;
        //sin.sin_addr.s_addr = htonl(ip);
        port = __port; 
        sin.sin_port = htons(port); 
        len_ssock = sizeof(sin);
        if(bind(server_sock,  reinterpret_cast<struct sockaddr *>(&sin), len_ssock) == ERROR)
        {
            perror("bind failure");
            exit(BIND_FAIL);
        }
        else
            std::cout << "Socket binded successful!: " <<  server_sock
            << "\nAddress family: "<< sin.sin_family 
            << "\nIP address: " << inet_ntoa(sin.sin_addr)
            << "\nPORT: " << ntohs(sin.sin_port)
            << std::endl;
        if (listen(server_sock, LISTENQ) == ERROR) 
        {
            perror( "Can't start to listen to." );
            exit(LISTEN_FAIL);
        }
        else 
            std::cout << "Listening..." << std::endl;
        
    }

    Socket(int __domain, int __type, int __protocol)
        :domain{__domain}, type{__type}, protocol{__protocol},
        server_sock{socket(__domain, __type, __protocol)}
    {
        if(errno == ERROR)
        {
            perror("Socket error");
            exit(SOCK_FAIL);
        }
    }

    ~Socket(){ close(server_sock);}

    void cycle()
    {
        std::cout << "Cycle\n";
        len_clsock = sizeof(struct sockaddr_in);

        while(1)
        {
            client_sock = accept(server_sock,  reinterpret_cast<struct sockaddr *>(&clin), &len_clsock);
            if(client_sock == ERROR)
            {
                printf("accept");
                exit(ACCEPT_FAIL);
            }
            else
                std::cout << "\nAccepted with client socket: " << client_sock 
                          << "\nsocked address: " << inet_ntoa(clin.sin_addr) 
                          << "\nsocket port: " << ntohs(clin.sin_port) << std::endl;
                

            char *name_host = (char*)malloc(sizeof(1024));
            
            int bytes_read = recv(client_sock, name_host, 1024, 0);
            if(bytes_read < 0) {delete name_host; close(client_sock); continue; }
            
            name_host = (char*)realloc(name_host, bytes_read);
            std::cout << "\nname of host: "<<  name_host << "\n";

            struct hostent *host_info;
            try
            {
                host_info = gethostbyname(name_host);
            }
            catch(std::exception err)
            {

                printf("gethostbyname");
                delete name_host, host_info;
                close(client_sock);
                continue;
            }

            char **addresses_net;
            try
            {
                addresses_net = host_info->h_addr_list;
            }
            catch(std::exception err)
            {
                printf("host_info->h_addr_list");
                delete name_host, host_info, addresses_net;
                close(client_sock);
                continue;
            }
            
            char **addresses_acci = new char*[host_info->h_length];
            struct in_addr* address;
            int num_addr;
            for (num_addr = 0; host_info->h_addr_list[num_addr] != 0; num_addr++)
            {
                addresses_acci[num_addr] = new char[16];
                address = (struct in_addr *)(host_info->h_addr_list[num_addr]);
                //std::cout << address << "\n";
                std::cout << inet_ntoa(*address) << "\n";
                strcpy(addresses_acci[num_addr], inet_ntoa(*address));
            }

            bytes_read = send(client_sock, addresses_acci[0], strlen(addresses_acci[0]), 0);
            if(bytes_read == -1) 
            {
                printf("send");
                delete name_host, host_info, addresses_net, addresses_acci;
                close(client_sock);
                continue;
            }

            // if(sendall(client_sock,  addresses_acci, num_addr) == 0)
            // {
            //     perror("sendall");
            //     exit(SEND_FAIL);
            // }
            delete name_host, host_info, addresses_net, addresses_acci;
            close(client_sock);
        }
    }

    int sendall(int sockfd, char** buf, size_t h_count, int flags=0)
    {
        int succ = h_count;
        for(int i = 0; i < h_count; i++)
            if(sendall(sockfd,  buf[i], strlen(buf[i]), flags) == ERROR)
                succ -= 1;
        
        return succ;
    }

    int sendall(int sockfd, char* buf, size_t len, int flags)
    {
        int total = 0;
        int n;
        while(total < len)
        {
            n = send(sockfd, buf+total, len - total, flags);
            if(n == -1) { break; }
            total += n;
        }
        return (n == -1 ? -1 : total);
    }

    int recvall(int sockfd, char *buf, size_t len, int flags)
    {
        int total = 0;
        int n;
        while(total < len)
        {
            n = recv(sockfd, buf + total, len - total, flags);
            if(n == -1 || n == 0) { break;}
            total += n;
        }
        return (n == -1 ? -1 : total);
    }
};