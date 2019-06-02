GeoBattle-Server program | 26.05.2019

Description:
----------

    This is the server application for a multiplayer planetary scale game - GeoBattle. Players build and develop their bases on a real world map using geolocation capabilities. The game will force not to sit still, and fight for the right to be the most successful.
    If you are reading this, then you have downloaded the necessary files to run your own server of this game. The developers are not opposed to making changes to the code, but after that they are not responsible for unstable work. Read the instructions carefully. Good luck in capturing the world!

-------------------------------------------------- ---------------------------

Main modules with description:
--------------------------------

    socket_server.py is the main server module. Listens to players requests and calls their handlers. Stores data about the committed attacks and changes in the game state in the last 10 seconds. Adds resources to players. Call structure: python3.6 socket_server.py -i <ip_addr> -p <port> -c <if you need to create a NEW database> -s <use tls encryption>.
    SslServer.py is a secondary server for updating certificates on player devices.
    startServer.py - starting the server and monitoring its operation. Call structure: python3.6 startServer.py -i <ip_addr> -p <port> -c <if you need to create a NEW database>
    stopServer.py is a simple server stop.
    newdb.py - create a database. Tables: Players, Sectors, Buildings, Units, Attacks.
    registration.py - is responsible for the registration / authorization of players. Performs mail verification.
    state.py - forms the FULL game state that is requested when the game starts.
    build.py - building / demolishing buildings.
    sectorBuild.py - building a new sector.
    ResearchEvent.py - improving the performance of aircraft, turrets and generators.
    addUnits.py - add units to the hangar
    getRating.py - information about the players' capital in monetary terms to compile a game rating.
    Fighting.py - creating a battle script.
    attack.py is a module for attacking foreign sectors.
    functions.py - support functions for the server.
    param_parser.py - module for accounting command line parameters
    serverFunctions.py - start-up functions and shutdown of certain server parts.
    cert.pem and key.pem - certificate and key for encryption.

-------------------------------------------------- -------------------------------------------------- --------

System requirements:
----------------------

    Linux operating system with 512mb ram. Packaged with Python version not lower than Python3.6.7. Additionally installed modules: ssl, psutil. Stable internet connection. Dedicated ip address.

-------------------------------------------------- -------------------------------------------------- --------

Startup Description:
------------------

0) Check your system requirements.
1) Copy the directory with all the files to an empty directory on the server computer with the ip address allocated.
2) Install the screen tool.
3) If you already have a ready-made database from previous launches, copy it to other files under the name main.db
4) Open a terminal and go to the directory to the server files.
5) Start the screen
6) Enter: python3.6 startServer.py -i <ip_addr> -p <port>
7) Press Ctrl + a and then d
8) The server is running! You can close ssh, if such a connection has taken place, the server will continue to work.

9) When you start the game, enter the details of your server in the Settings tab.

-------------------------------------------------- -------------------------------------------------- -------------------

About the authors:
    The project was created as part of the It School Samsung program by graduates: Podkovyrovy Demyan, Karandashov Vladislav and Temnenkov Maxim. You can send your bug reports and suggestions to geobattleit@gmail.com. The newest version of the server at the link https://github.com/Dx18/ServerGeobattle. The newest version of the client is available at https://github.com/Dx18/GeoBattle.
