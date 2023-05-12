# CHAT DS WEB APP - CREATED AND OWN BY ALEX BUI

## This is the source code for the web application

This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 13.1.2. You have to install NPM and NodeJS v16 first.

## Init project
Run `npm install` to initialize the project.

## Development server

Run `ng serve --port 4200 --host 0.0.0.0` for a dev server. Navigate to `http://your_ip_addr:4200/`. You can change port 4200 to any ports.


## Need to open jupyter to be loaded into iframe
jupyter notebook --generate-config
c.NotebookApp.tornado_settings = {
    'headers': {
        'Content-Security-Policy': "frame-ancestors 'self' *"
    }
}