Consensus algorithm for replicated state machines.

UPDATE - Visualize the formation of hashgraph.

UPDATE - This project is now running on system level, will soon update the running model on distributed systems. 

In first phase we are focusing on implementing a system level network and a GUI to visualize transactions [ Only needed for human satisfaction, not at all needed to build any application on hashgraph], in later phase we'll try to build this on TCP/IP level to take it to real world scenario.

Make sure you have read all the whitepapers on this link https://www.swirlds.com/whitepapers/ and know the proper implementation strategy.

Dependencies - 

     1.Install PyNaCl using pip3 command - [ PyNaCl uses libsodium https://download.libsodium.org/libsodium/ at its core and the following link will give the bundled copy  of its python implementation  https://pypi.python.org/pypi/PyNaCl#downloads ] 

     2.Install PyYaMl using pip3 command - [ PyYAML is a YAML parser and emitter for Python  https://pypi.python.org/pypi/PyYAML/3.12 ] 
     
     3.Bokeh for plotting the hashgraph. [ use pip3 command for straight forward download along with dependencies]
     
   Running the code - 
   
   
     1. Download the project and in terminal run -  bokeh serve --show draw.py --args << no_of_nodes_needed >>
     
     
     2. If incase you need a fixed number of events run start.py from master branch.
