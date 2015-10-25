%*
%80 edges
Expected result
concept(1)=("CDC73" ,"CHD1" ,"CTR9" ,"HOT1" ,"CKA2" ,"SPT16" ,"POB3" ,"PRT1") X ("CKB2" ,"CKA1" ,"CKB1"). 
concept(2)=("PAF1" ,"CDC73") X ("LEO1" ,"RTF1", "SPT16" ,"CTR9" ,"POB3").
concept(3)=("CKB2" ,"CKA2" ,"SSA3" ,"SSA4" ,"CKA1" ,"HOT1" ,"PPZ1" ,"CHD1") X ("YKL088W").
concept(4)=("CKA2" ,"CKB2" ,"ROK1" ,"YLR003C" ,"CKB1" ,"RRP7") X ("UTP22"). 
clique(5,"CKB2" ,"CKB1" ,"RPG1" ,"NIP1").
clique(6,"CKA2", "SPT16","CTR9").
clique(7,"CTR9" ,"RTF1" ,"LEO1").
clique(8,"CHD1" ,"HOT1" ,"SSA4").
clique(9,"ROK1" ,"RRP7" ,"YLR003C").
clique(10,"POB3" ,"SPT16" ,"HHF1").
concept(11)=("CKA1") X ("CKB1" ,"CKB2"). 
concept(12)=("PRT1") X ("RPG1" , "NIP1"). 
concept(13)=("POB3") X ("CKA2").
clique(14,"RTF1","CKA1").
clique(15,"SSA4","CKB2").
clique(16,"CDC73","CKA2").
clique(17,"PAF1","CDC73").
clique(18,"CHD1","CKA2").
clique(19,"PPZ1","SSA3").
*%

edge("POB3","SPT16").
edge("POB3","CDC73").
edge("POB3","HHF1").
edge("POB3","CKB2").
edge("POB3","CKA2").
edge("POB3","PAF1").
edge("POB3","CKA1").
edge("POB3","CKB1").
edge("SPT16","CDC73").
edge("SPT16","CTR9").
edge("SPT16","HHF1").
edge("SPT16","CKB2").
edge("SPT16","CKA2").
edge("SPT16","PAF1").
edge("SPT16","CKA1").
edge("SPT16","CKB1").
edge("CDC73","CTR9").
edge("CDC73","CKB2").
edge("CDC73","CKA2").
edge("CDC73","LEO1").
edge("CDC73","PAF1").
edge("CDC73","CKA1").
edge("CDC73","RTF1").
edge("CDC73","CKB1").
edge("CTR9","CKB2").
edge("CTR9","CKA2").
edge("CTR9","LEO1").
edge("CTR9","PAF1").
edge("CTR9","CKA1").
edge("CTR9","RTF1").
edge("CTR9","CKB1").
edge("SSA4","CKB2").
edge("SSA4","YKL088W").
edge("SSA4","CHD1").
edge("SSA4","HOT1").
edge("CKB2","PRT1").
edge("CKB2","YKL088W").
edge("CKB2","CKA2").
edge("CKB2","UTP22").
edge("CKB2","RPG1").
edge("CKB2","NIP1").
edge("CKB2","CHD1").
edge("CKB2","HOT1").
edge("CKB2","CKA1").
edge("CKB2","CKB1").
edge("PRT1","RPG1").
edge("PRT1","NIP1").
edge("PRT1","CKA1").
edge("PRT1","CKB1").
edge("SSA3","YKL088W").
edge("SSA3","PPZ1").
edge("YKL088W","CKA2").
edge("YKL088W","PPZ1").
edge("YKL088W","CHD1").
edge("YKL088W","HOT1").
edge("YKL088W","CKA1").
edge("CKA2","UTP22").
edge("CKA2","CHD1").
edge("CKA2","CKA1").
edge("CKA2","CKB1").
edge("LEO1","PAF1").
edge("LEO1","RTF1").
edge("UTP22","RRP7").
edge("UTP22","ROK1").
edge("UTP22","CKB1").
edge("UTP22","YLR003C").
edge("RPG1","NIP1").
edge("RPG1","CKB1").
edge("NIP1","CKB1").
edge("RRP7","ROK1").
edge("RRP7","YLR003C").
edge("PAF1","RTF1").
edge("CHD1","HOT1").
edge("CHD1","CKA1").
edge("CHD1","CKB1").
edge("HOT1","CKA1").
edge("HOT1","CKB1").
edge("CKA1","RTF1").
edge("CKA1","CKB1").
edge("ROK1","YLR003C").
