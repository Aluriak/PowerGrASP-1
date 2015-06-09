%*
%106 edges
Expected result
% 5 connected components
{"ARP4","YML041C","SWR1","RVB2,"RVB1","ARP5","PIL1","HTA2","HHF2","HTA1","NAP1","HTB1","POB3","SPT16","HHT2",
 "HHT1","HHF1","HTB2","ORC6","ORC2","HTZ1","RTT102","ORC1","ORC5","ORC4","HHO1","ORC3","SWI3","SWI1","SNF2","SNF6","SNF5"}.  
{"HPC2","HIR1","HIR2","HIR3"}. 
{"SWI4","SWI6"}. 
{"SNF1","SNF4"}. 
{"ARP2","ARP3"}.  
 

1("HHF1" ,"HTB2" ,"HTB1" ,"HHT1" ,"HTA1" ,"NAP1" ,"HHT2" ,"HHF2") X ("HTA2" ,"POB3" ,"SPT16"). 
2("ORC5" ,"ORC4" ,"HTB2" ,"ORC3" ,"HHF1") X ("ORC2" ,"ORC6" ,"ORC1").
3("ARP5" ,"ARP4" ,"PIL1" ,"YML041C" ,"SWR1") X ("RVB2" ,"RVB1"). 
4("RTT102" ,"SNF6", "SNF5" ,"SWI3") X ("SWI1" ,"SNF2").
5("NAP1", "HTB2", "HTB1","HTZ1").
6 ("ORC2","ORC6","ORC1").
7 ("SPT16,"HTA2","POB3").
8 ("HHF1","HTB2","HHT1").
9("HTB2","ORC4","ORC5").
10("HHF1","HHF2","HHT2").
11("SWR1","ARP4","YML041C").
12("ORC3") X ("ORC5","ORC4").
13("RTT102") X ("HHF1","HTB2"). 
14("HTA2") X ("ORC6","ORC2").
15("HHT2") X ("HHT1").
16 ("HHF2") X ("HTB2").
17("NAP1") X ("HHT1").
18("HHF1") X ("HTB1").
19("ARP5") X ("HTA2").
20("ORC6") X ("HHO1").
21("SNF2","SWI1").
22("RVB2","RVB1").
23("ARP5","ARP4").
24("NAP1","HTA1").
25("RTT102","SWI3").
26("SNF6","SWI3").
27("PIL1","SWR1").
  28("HIR1" ,"HIR2" ,"HIR3") X ("HPC2").
  29("ARP2") X ("ARP3").
  30("SNF1") X ("SNF4"). 
  31("SWI4") X ("SWI6"). 

*%

edge("HHO1","ORC6"). 
edge("ORC3","ORC1"). %2
edge("ORC3","ORC4"). 
edge("ORC3","ORC6"). %2
edge("ORC3","ORC2"). %2
edge("ORC3","ORC5"). 
edge("HTB1","POB3"). %1
edge("HTB1","SPT16"). %1
edge("HTB1","HTZ1"). %5
edge("HTB1","HHF1").
edge("HTB1","HTB2"). %5
edge("HTB1","HTA2"). %1
edge("HTB1","NAP1"). %5
edge("SWI4","SWI6").
edge("YML041C","SWR1").
edge("YML041C","RVB2").
edge("YML041C","RVB1").
edge("YML041C","ARP4").
edge("POB3","SPT16").
edge("POB3","HHT2").
edge("POB3","HHT1").
edge("POB3","HHF1").
edge("POB3","HTB2").
edge("POB3","HTA2").
edge("POB3","HHF2").
edge("POB3","HTA1").
edge("POB3","NAP1").
edge("SWI3","SNF6"). 
edge("SWI3","SWI1").
edge("SWI3","SNF2").
edge("SWI3","RTT102"). 
edge("SNF6","SWI1").
edge("SNF6","SNF2").
edge("SPT16","HHT2").
edge("SPT16","HHT1").
edge("SPT16","HHF1").
edge("SPT16","HTB2").
edge("SPT16","HTA2").
edge("SPT16","HHF2").
edge("SPT16","HTA1").
edge("SPT16","NAP1").
edge("ORC1","HHF1").
edge("ORC1","ORC4").
edge("ORC1","HTB2").
edge("ORC1","ORC6").
edge("ORC1","ORC2").
edge("ORC1","ORC5").
edge("SWR1","RVB2").
edge("SWR1","PIL1"). 
edge("SWR1","RVB1").
edge("SWR1","ARP4").
edge("RVB2","PIL1").
edge("RVB2","RVB1"). 
edge("RVB2","ARP5").
edge("RVB2","ARP4").
edge("PIL1","RVB1").
edge("RVB1","ARP5").
edge("RVB1","ARP4").
edge("HPC2","HIR2").
edge("HPC2","HIR1").
edge("HPC2","HIR3").
edge("SWI1","SNF2"). 
edge("SWI1","SNF5").
edge("SWI1","RTT102").
edge("SNF2","SNF5").
edge("SNF2","RTT102").
edge("HHT2","HHT1"). 
edge("HHT2","HHF1").
edge("HHT2","HTA2").
edge("HHT2","HHF2").
edge("SNF4","SNF1").
edge("HTZ1","HTB2").
edge("HTZ1","NAP1").
edge("HHT1","HHF1").
edge("HHT1","HTB2").
edge("HHT1","HTA2").
edge("HHT1","NAP1"). 
edge("HHF1","HTB2").
edge("HHF1","ORC6").
edge("HHF1","ORC2").
edge("HHF1","RTT102").
edge("HHF1","HTA2").
edge("HHF1","HHF2").
edge("ARP3","ARP2").
edge("ORC4","HTB2").
edge("ORC4","ORC6").
edge("ORC4","ORC2").
edge("ORC4","ORC5").
edge("HTB2","ORC6").
edge("HTB2","ORC2").
edge("HTB2","RTT102").
edge("HTB2","HTA2").
edge("HTB2","ORC5").
edge("HTB2","HHF2"). 
edge("HTB2","NAP1").
edge("ORC6","ORC2").
edge("ORC6","HTA2").
edge("ORC6","ORC5").
edge("ORC2","HTA2").
edge("ORC2","ORC5").
edge("ARP5","ARP4"). 
edge("ARP5","HTA2").
edge("HTA2","HHF2").
edge("HTA2","HTA1").
edge("HTA2","NAP1").
edge("HTA1","NAP1"). 
