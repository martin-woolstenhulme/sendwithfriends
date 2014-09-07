HOST=104.131.135.52
scp -i id_rsa application.py root@104.131.135.52:
rsync -Pav -e 'ssh -i id_rsa' twilio/ root@104.131.135.52:twilio/
rsync -Pav -e 'ssh -i id_rsa' templates/ root@104.131.135.52:templates/
rsync -Pav -e 'ssh -i id_rsa' static/ root@104.131.135.52:static/
rsync -Pav -e 'ssh -i id_rsa' Utils/ root@104.131.135.52:Utils/
rsync -Pav -e 'ssh -i id_rsa' db_schema/ root@104.131.135.52:db_schema/
rsync -Pav -e 'ssh -i id_rsa' Handlers/ root@104.131.135.52:Handlers/
