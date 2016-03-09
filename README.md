# neventGeneratorPy

Python implementation of neventGenerator. Usage:

(server side)   `zmqGenerator.py <NeXus file> <port>`
(receiver side) `zmqReader.py tcp://<ip>:<port>`
(trigger side)  `telnet <ip> 8123 -> run/pause`

**zmqGenerator** loads <NeXus file> and translate in event format (or generates
a mock event) and wait for trigger to send *run* message. **zmqReader** keeps
listening for messages

