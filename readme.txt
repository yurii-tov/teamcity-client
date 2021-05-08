* CLI client for TeamCity based on pyteamcity


** Features
   - Show brief info about build types
   - Show brief info about last build


** Installation
   - Place shortcut to startup script into .bashrc:
     (Example)
     function teamcity() { "c:/Users/Jury/work/teamcity-client/teamcity.sh" "$@" | iconv -f cp1251 -t utf-8 ; }
   - Read help:
     $ teamcity -h
