cd /home/blitz/Documents/BlitzVision
touch /home/blitz/bvscript-ran.txt
sleep 15
id >> /home/blitz/bvscript-uid.txt
/usr/bin/python3.11 -c "import sys; print(sys.path)" > /home/blitz/pypath.txt
/usr/bin/python3.11 core/dispatcher.py > /home/blitz/pylog.txt 2>&1
