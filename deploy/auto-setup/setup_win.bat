@echo off

rem Create a new group for PowerDNS-Admin
net localgroup gundnsadmin /add

rem Create a user for PowerDNS-Admin
net user gundnsadmin /add /passwordchg:no /homedir:nul /active:yes /expires:never /passwordreq:no /s

rem Make the new user and group the owners of the PowerDNS-Admin files
icacls "C:\path\to\powerdns-admin" /setowner "gundnsadmin"

rem Start the PowerDNS-Admin service
net start powerdns-admin

rem Enable the PowerDNS-Admin service to start automatically at boot
sc config powerdns-admin start= auto
