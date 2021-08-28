# COVID-19-Agent-Based-Models

This repository contains the three variations of our COVID-19 Agent-Based Model developed at the System Modeling and Simulation Laboratory (Department of Computer Science, University of the Philippines Diliman). The variations are as follows: 1) Agent-Based Model for Quezon City (a coronavirus hot-spot), 2) a "generic" model with contact probabilities, and 3) a multi-space model with contact probabilities. All these models are based on the Age-Stratified, Quarantine Modified SEIR with Non-linear Incidence Rates [1]. The contact probabilities were taken from the study of Prem et al. [2]

Model dependencies: 
- Mesa 
- MesaGeo (for variation 1 only)
- Pandas 
- Numpy

The results of our studies on COVID-19 modeling may be accessed in xxx.

[1] Minoza JMA, Sevilleja JE, de Castro R, Caoili SE, Bongolan VP. Protection after Quarantine: Insights from a Q-SEIR Model with Nonlinear Incidence Rates Applied to COVID-19. medRxiv; 2020. DOI: 10.1101/2020.06.06.20124388.

[2] Prem K, Cook AR, Jit M (2017) Projecting social contact matrices in 152 countries using contact surveys and demographic data. PLOS Computational Biology 13(9): e1005697. https://doi.org/10.1371/journal.pcbi.1005697
