# whet
Aquarium controller for raspberry pi and PCA9685
Developing on pi 3B

Written in python.
Using things like sockjs, tornado, liking websockets and probably some javascript coming up, still making up my mind.


Features:
Dimming - constant current led drivers that are dimmable via pwm signal.
Maybe doing relays.




Nginx config for reverse proxy and https:

        location ^~ /web {
               auth_basic "Restricted";
               auth_basic_user_file /config/nginx/.htpasswd;
               include /config/nginx/proxy.conf;
               proxy_pass http://pi:8080;
       }
        location ^~ /chat {
               auth_basic "Restricted";
               auth_basic_user_file /config/nginx/.htpasswd;
               include /config/nginx/proxy.conf;
               proxy_pass http://pi:8080;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "upgrade";
                proxy_set_header Host $host;
       }

#proxy.conf
client_max_body_size 10m;
client_body_buffer_size 128k;

#Timeout if the real server is dead
proxy_next_upstream error timeout invalid_header http_500 http_502 http_503;

# Advanced Proxy Config
send_timeout 5m;
proxy_read_timeout 240;
proxy_send_timeout 240;
proxy_connect_timeout 240;

# Basic Proxy Config
proxy_set_header Host $host:$server_port;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto https;
proxy_redirect  http://  $scheme://;
proxy_http_version 1.1;
proxy_set_header Connection "";
proxy_cache_bypass $cookie_session;
proxy_no_cache $cookie_session;
proxy_buffers 32 4k;
