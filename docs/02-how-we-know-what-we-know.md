# Chapter 2: How we know what we know about HIV

## Abstract

What we know about HIV is directly tied to how we know what we know. In **Chapter 2** I summarize select methods used in key papers throughout the past 40 years of HIV research. These methods were used to detect HIV, to measure HIV gene expression by way of mRNA or protein abundances, and to measure HIV sequence heterogeneity. Clinical interrogation of HIV information is also discussed. Points to consider:

- how much information is recovered with a given method,

- how many samples can be processed at a given time, and

- how progressively newer methods improved on pervious methods.

## Introduction – reading HIV information

The methods used to study HIV have changed drastically over the last 40 years since the first AIDS case report (CDC 1981). Progress came from parallel advances in both computing hardware, nucleic acid sequencing and computer software methods to analyze and handle progressively larger sequencing datasets. Details of the computational hardware side of these advances are outside the scope of this dissertation. Regarding nucleic acid sequencing, this time can be very roughly divided into pre-sequencing and post-sequencing eras. Protein sequencing falls outside of the scope of the present dissertation and so is not discussed.

## The pre-sequencing era of HIV informatics is marked by qualitative datasets

The pre-sequencing era was a time around the discovery of HIV, but before the wide adoption of nucleic acid sequencing methods to directly interrogate experimental systems or clinical samples. However, it is important to understand that the major advances in the pre-sequencing era were founded on the growing availability of high-quality HIV-1 and related viral genomes. These were part of several disjointed HIV genome projects, and here these are explicitly called HIV sequencing projects, after the technical usage of a biological entity’s genome sequencing project (Shendure et al. 2017). Shortly after one of the first HIV genomes was stabilized as a molecular clone (Hahn et al. 1984), the first HIV-1 reference genome was completed in 1985 (Ratner et al. 1985). It is represented as either GenBank:K03455.1 or RefSeq:NC_001802.1. Lower-throughput qualitative assays were founded on this seminal HIV sequence information.

#### Polymerase chain reaction (PCR)

Polymerase chain reaction (PCR) is a method used to amplify targeted regions of DNA. It was one of the first molecular methods used to interrogate HIV as HIV proviral sequences. Most often, prior information is necessary to optimize each PCR. The user can select which sequences of DNA to amplify based off known sequence. Short (approximately 20 nucleotides long) homologous sequences in the forward and reverse orientation are used to prime DNA polymerization. These form a primer window, which allows for the amplification of everything between the ends of the inward facing primers and copying of the primer spanning region. This is analogous to a pair of binoculars which enable the user to view everything within the field of view, not including the black field of view taken up by the binoculars.

The advent of thermostable Taq (Saiki et al. 1988) and thermocyclers helped bring PCR into labs across the world. For his work and for inventing the PCR method, Kary B Mullis was awarded half of a Nobel Prize in Chemistry in 1993. Benefits of PCR include sensitivity to detect low copy number target sequences, as well as specificity for sequences with homology to primers used. Limitations of PCR include if a target is in an area with extremely low or high GC content, which may hinder amplification. Example, GC-rich sequences do not amplify, while AT-rich sequences amplify (sometimes too) well. Areas with secondary structure may not amplify well, although this is not believed to be a major problem for most DNA sequences. PCR using commercially available kits can amplify ACGT-containing sequences because kits include dA, dC, dG, and dT. Base modifications like A methylation, C methylation or C hydroxymethylation are effectively erased when a target region is amplified. DNA damage might be overwritten, which may affect validity of downstream applications. The DNA polymerases used for PCR have an intrinsic fidelity and processivity. Fidelity in the context of a nucleic acid polymerase refers to how faithfully information encoded in a template is copied to newly synthesized strands. Procesivity refers to the ability of an enzyme to remain on its template, enabling continued synthesis. The first available DNA polymerases had lower fidelity and processivity, and these limited the ability to amplify sequences longer than 5-10 kilobase (kb). Newer polymerases can amplify DNA to &gt;40kb. In contrast to cellular genomic DNA replication, *in vitro* DNA polymerases lack proofreading, and so they can introduce errors into sequences during PCR. Errors are subsequently amplified with progressive PCR cycles. While experiments can be designed around most of PCR’s limitations, such avoidance has precluded work vital to the study of HIV.

Nested PCR combines at least two pairs of primers approximating the target window to be amplified, and two sets of cycles to increase sensitivity of detecting specific analytes (Green and Sambrook 2019). This has been important for detecting HIV in clinical samples, especially in the context of antiretroviral therapy and low plasma viral load. Until relatively recently it was not tractable to amplify nearly full-length HIV. Newer protocols leveraging improved Taq and RT isoforms and nested PCR have redressed this successfully.

#### Reverse transcription with reverse transcriptase (RT)

Importantly, PCR can efficiently amplify DNA targets. This is because DNA has less secondary structure compared to RNA. DNA is also less susceptible to degradation in normal laboratory conditions. Until recently, to sequence RNA, one needed to convert RNA to DNA. This was done with viral reverse transcriptase enzymes. The importance of this work was recognized as Howard Martin Temin, David Baltimore, and Renato Dulbecco split the Nobel prize in Physiology or Medicine in 1975 "for their discoveries concerning the interaction between tumor viruses and the genetic material of the cell." An important tumor virus studied was Moloney murine leukemia virus (MMLV), a retrovirus with reverse transcriptase (RT) enzymatic activity. Commercial RT has been mostly MMLV (Zucha et al. 2020). An important technical limitation of RT is the relatively high error rate compared to DNA polymerase in PCR. RT error rates in different viruses can vary between about 1 in 10,000 to 1 in 100,000 (Menéndez-Arias 2009). cDNA made from RT could be subjected to subsequent PCR.

RT PCR protocols can differ, but they can generally be divided into two flavors: one-step and two-step. One-step combines RT with PCR in a single tube. Users must supply target-specific primers. This is better suited for detecting a single target from a given sample. Two-step RT PCR, which is better for detecting multiple targets in a sample, separates the RT step and the PCR step. Primers may include oligo-dT, random hexamer, or target-specific primers. Random primers can have more off-target amplification artifacts. RT qPCR (q is for “quantitative”) offered a semiquantitative improvement but is similarly limited by primer specificity which limits target sequence amplification.

These methods are all endpoint assays. The measurand is the intensity of a band or fluorescence at one or multiple timepoints. You never directly evaluate sequence info. Instead, you deduce sequence homology based on ability to detect amplification products at expected weights in absence of other non-specific bands. There remains no way to differentiate between a true positive and a false positive which happens to amplify near a given weight on a gel. qPCR is more sensitive, but remains an indirect endpoint assay.

## The post-sequencing era of HIV informatics is marked by quantitative datasets

The post-sequencing era is defined by the growing adoption of increasingly higher-throughput and cheaper sequencing methods to detect HIV across various sample matrices (e.g., plasma, venous blood, tissue), usually paired with mapping derivative sequences back to an HIV reference genome (HXB2). This is explicitly called resequencing (Shendure et al. 2017), and here I call it HIV resequencing v1.0 to distinguish this as work done prior to the advent of HIV Informatics. The post-sequencing era proceeded roughly sequentially:

1.  Pairing reverse transcription with PCR with short-read sequencing

2.  Pairing reverse transcription with PCR with multiplexed short-read sequencing

3.  Pairing reverse transcription with PCR with long-read sequencing (my work and others’)

4.  Pairing reverse transcription with PCR with multiplexed long-read sequencing (my work and others’)

In addition to basic and translational science, HIV sequence heterogeneity has also been used to track HIV transmission with emerging molecular epidemiology methods. HIV transmission was demonstrated in a forensic case by Metzker et al. 2002 (Metzker et al. 2002). Because of the risk of perpetrating HIV stigma, concern of community members about HIV criminalization by overextending scientific results has been expressed (https://www.aidsmap.com/news/jan-2021/molecular-hiv-surveillance-friend-or-foe).

## HIV expression in select HIV models


Measuring HIV is challenging due to HIV’s myriad forms, reviewed in Chapter 7 (Gener 2021b). “HIV gene expression” as a concept can be problematic because of the phrase’s relative ambiguity. Investigators might mean to describe abundance of HIV mRNA, HIV DNA, HIV protein. In this dissertation I focused on measuring HIV sequence information and/or HIV mRNA abundance.

Early work, for example Schwartz et al. elaborated important cell culture models for studying HIV mRNA expression. Human immunodeficiency virus type 1 HLtat cells (ARP-1293) are cells which stably express a truncated version of Tat, sometimes called Tat-1. (This will be revisited in Chapter 6 (Gener 2021a) with GENER13). This cell line was important to be able to easily study gene expression of proteins driven by the HIV-1 LTR promoter. Another cell line, Human immunodeficiency virus type 1 HLfB cells (ARP-1300) - (Hadzopoulou-Cladaras et al. 1989; Mermer et al. 1990) (<https://www.hivreagentprogram.org/Catalog/cellBanks/ARP-1300.aspx>) was used to demonstrate that mRNAs containing a Rev Response Element (RRE) (**Chapter 1** **[Chapter 1 Figure 5](01-what-we-believe-about-hiv.md#figure-5): HIV-1 NL4-3 Rev Response element**) were positively modulated by Rev protein. Products of non-RRE mRNAs were negatively regulated by Rev.

Transfecting cells (HeLa, CD4+ T cells, others) with HIV cDNA clones was a common way to study the effects of the first HIV proteins studied. A limitation of this approach was susceptibility of cloned mRNAs’ transcripts to additional splicing which might not be physiological. This highlights the difficulty in distinguishing between co-transcriptional and post-transcriptional splicing. I did not address this relationship in this dissertation, but it is relevant for the splicing patterns described in Chapter 6.

Once an HIV genome was available, primers could be designed to amplify and detect HIV. Such HIV PCR was more useful in experimental systems which began with infection of an HIV-negative sample with a known HIV strain, for example, NL4-3. Partly because of HIV’s inherent sequence variability, the use of PCR amplification to measure HIV in clinical samples was limited. Other considerations include fidelity and processivity of both RT and DNA polymerases used in RT PCR, as well as the availability and cost of sequencing methods.

## HIV tropism

Methods used to study HIV tropism *in vitro* include cell culture and HIV infection determined by reverse transcriptase activity, p24 antigen detection, and PCR. Methods used to study HIV tropism *in vivo* included immunohistochemistry and *in situ* hybridization. (Table 3.8 (Levy 2007)). Importantly, sequencing has only recently been used to follow HIV across different potential reservoirs.

## Clinical HIV testing

While the detailed clinical management of HIV/AIDS patients falls outside the scope of this dissertation, HIV diagnosis is within the scope of HIV information. As such, I will describe how HIV diagnostics and monitoring have developed and relate them back to the kinds of information measured in more basic studies of HIV.

Pre-sequencing era tests relied on a patient’s immune responses to HIV by detecting a patient’s humoral responses in the form of antibodies against HIV antigens, and later incorporated detection of HIV antigens. Prior to addition of p24, tests in the context of AIDS were more likely to be false negative. This was because immunosuppressed patients sometimes lost their antibody responses.

Sequencing is not generally used for HIV diagnosis. However, HIV mRNA information is assayed during HIV treatment. These areas of overlap include viral load measurement (which is not sequencing) and HIV genotyping (which is sequencing).

## Development of diagnostic HIV testing

Concurrent with the isolation of a putative AIDS-causing virus (Barré-Sinoussi et al. 1983; Gallo et al. 1983) and the naming of HIV (AP 1986), there was high demand for an “AIDS test” for at least a couple of reasons. One was to diagnose AIDS in patients to prevent the spread of the AIDS virus. Another was to protect healthcare systems’ blood supplies from contamination. A clinical test for AIDS based on measuring analytes would ultimately never be developed because of the need to integrate acute clinical information with a patient’s past medical history to ascertain a patient’s risk factor(s) for acquiring HIV with measurable analyte(s). However, tests could be developed for an AIDS virus (Alexander 2016).

Once the biomedical community realized that such a deadly bloodborne pathogen could be transmitted in unscreened blood/blood products, there was an immediate need to screen pooled blood/blood products for the AIDS-causing virus. Tests were developed to screen pooled blood/blood products. They worked by detecting antibodies against immobilized HIV antigens. These first assays were sensitive, but not specific. While there were some false positives, the benefit of removing contaminated blood products outweighed the harm of delivering a false positive to a patient at risk of acquiring AIDS. Positive results were given to blood donors, and these people were prohibited from future donations. Since the first HIV tests were not clinical tests, physicians could not order them for their patients at risk of developing or suspected of having AIDS. At that time there was no treatment for HIV to prevent AIDS, however some AIDS-defining conditions could be treated.

HIV diagnostic tests were developed, progressing through multiple iterations. The first iterations focused on detecting HIV-1 M B HTLV-III/HXB2/LAV sequence only, then HIV-2 was added, and next HIV-2 and HIV-1 O. Today, fourth-generation enzyme immunoassays detect antibodies and HIV-1 p24 antigen. Alternative testing includes rapid third-generation enzyme immunoassays that detect antibodies only (Ghosn et al. 2018). Rapid tests are lateral flow assays which give results in 10-20 minutes, and can be done practically anywhere (as opposed to in the confines of a lab). Other assays require specialized equipment running multiple samples a a time and can only be done in specialized labs. A shortcoming of rapid HIV tests is an inability to detect HIV during the acute phase before sufficient production of antibodies (Ghosn et al. 2018). While 4<sup>th</sup> generation assays are more expensive, their utility in at risk populations can justify their use. Serology and antigen detection is generally preferred for screening adults. In the context of neonatal HIV diagnosis and need for viral load as diagnosis instead. This is because of maternal anti-HIV antibodies for the first several months postpartum which might be detected as false positive neonate. In 2006, the CDC recommended that HIV testing be considered as part of routine care (Alexander 2016).

## HIV viral load

HIV viral load (VL) is used for initial assessment after HIV diagnosis in adults and for subsequence monitoring. VL is generally not used for adult or pediatric HIV diagnosis. However, VL is used in *newborn* HIV diagnosis. Current methods to measure HIV viral load are diverse, reviewed elsewhere (Ginocchio 2001). TaqMan probes are used for some VL assays. These probes can tolerate some heterogeneity, and until recently have been a preferred method to determine HIV VL in clinical samples. PCR may also be used. Sequencing is generally not used to assess VL. Commercial HIV VL assays are generally specific for HIV-1 (Dube MP. , Stein JH. 2018).

HIV VL is important for initial assessment because 1.) a patient's pre-ART viral load level and 2.) the magnitude of viral load decline after initiation of ART both provide prognostic information about the probability of disease progression (Murray et al. 1999). Decreases in HIV VL after initiating antiretroviral therapy were associated with decreased risk of progression to AIDS (Marschner et al. 1998; Murray et al. 1999; Thiébaut et al. 2000).

## HIV Genotyping

In resource-rich settings, one of the first things that is done after a person is diagnosed with HIV is that ART drug resistance profiling is ordered. This is usually done by way of virus (HIV) genotyping. Genotypic resistance testing may be used to stage HIV disease and to assist in the selection of ART regimens (Dube MP. , Stein JH. 2018). (Grading scheme: Strength of Recommendation + Quality of Evidence for Recommendation. AII “A2”, where A is Strong recommendation for the statement; and 2 or **II is** “One or more well-designed, non-randomized trials or observational cohort studies with long-term clinical outcomes”. HIV genotyping is indicated prior to treatment initiation or change, treatment failure, if ART initiation is delayed, or if genotyping is otherwise clinically indicated. (<https://clinicalinfo.hiv.gov/en/table/table-3-laboratory-testing-schedule-monitoring-people-hiv-and-after-initiation-antiretroviral>) (Dube MP. , Stein JH. 2018). Genotyping is based on sequencing cDNA from RT PCR of partial HIV-1 pol, (PR, RT) and more recently complete pol (PR + RT + IN).

HIV genotyping has its limitations and advantages. To be successful at HIV genotyping, there must be enough HIV mRNA analyte in the sample matrix. This usually means HIV RNA levels greater than 500 to 1,000 copies/mL. Otherrwise, viral amplification for resistance testing may not be successful **(BII)**.” Source: <https://clinicalinfo.hiv.gov/en/guidelines/adult-and-adolescent-arv/baseline-evaluation?view=full> (Dube MP. , Stein JH. 2018). Access to sequencing facilities in many settings currently limits the implementation of HIV genotyping clinically. When Sanger sequencing is used, Sanger is known to be insensitive to variants occurring less than 10-20% of the time (https://aidsinfo.nih.gov/guidelines/html/1/adult-and-adolescent-arv/6/drug-resistance-testing). An advantage of Sanger though is relative cheap cost per sample when processed one at a time (as opposed to multiplexed with NGS/2<sup>nd</sup> generation sequencing or 3<sup>rd</sup> generation sequencing). Limitations from PCR include primers biasing resistance profiling to the window of observation between the primers. Variations on PCR including nested PCR are often used to amplify HIV sequences for sequencing. Because HIV exhibits formidable sequence heterogeneity even over relatively conserved regions in its genome, the use of PCR primers selects against sequences which differ markedly from primer-complimentary sequences. As mentioned before, a nontrivial consideration for HIV genotyping is sequencing samples with sufficient analytes (HIV genome equivalents) to yield sequence. Acute cases of HIV infection generally have more than enough HIV to recover sequence. Chronic cases of HIV may or may not depending on the amount of latency in the patient when sampled. Other potential PCR concerns of GC bias are not immediately relevant for HIV-1, because the average GC content across the HIV genome approximates that seen in the host genome (Gener, unpublished). Proviral DNA testing is performed rarely (source: <https://clinicalinfo.hiv.gov/en/table/table-3-laboratory-testing-schedule-monitoring-people-hiv-and-after-initiation-antiretroviral>) (Dube MP. , Stein JH. 2018).

An important consideration in NGS-based HIV genotyping is the risk of averaging out HIV heterogeneity for the sake of a complete genome assembly. Often, consensus sequences derived from individual patient samples collected at a given time are provided, and variants are called for subsequence resistance analyses (e.g., comparing to the Stanford HIV Drug Resistance database). Reads mapping to a region might be filtered out if they don’t contribute to the most common sequences. These might still represent viable virus subpopulations which may contribute to a patient’s HIV drug resistance. This limitation can be redressed by applying a second mapping step after the first assembly to collect secondary variability.

Treatment success for first-line ART is defined as reaching undetectable viral load by 48 weeks after ART initiation, where undetectable is defined as a plasma viral load below 50 copies per mL (Ghosn et al. 2018). Functionally, sustained viral loads &lt;200 copies per mL are another commonly used threshold.

## Writing HIV information

It is important to note that cloning each of the first 9 HIV gene products (Gag, Gag-Pol as Pol, Vif, Vpr, Vpu, Env, Nef, and spliced Tat and Rev) and subsequent drug and vaccine development began during the pre-sequencing era. Efforts generally did not consider additional HIV sequence heterogeneity beyond the initial information in HXB2-like HIV-1s. A notable exception was when considering resistance to fusion inhibitor maraviroc, which is limited to HIV patients with R5-tropic HIV-1s, which is often seen earlier during the natural course of infection (see **Chapter 1**). Another exception included the discovery and concurrent justification of HIV’s 10<sup>th</sup> gene product: antisense protein (Cassan et al. 2016). In that study, an open reading frame (ORF) which appeared to be a relatively new addition to some HIV-1 M group B subgroup strains was noted.

HIV RT generated HIV cDNA which could be cloned into bacterial or other expression vectors. Attention to promoter selection and codon optimization in the case of protein expression in non-mammalian systems was necessary. The availability of more and more restriction enzymes over time increased the ability of molecular biologists to manipulate HIV clones. As such, the synthetic clone NL4-3 has become a molecular biology staple and is still commonly used in lentivirus vectors and mammalian expression vectors. An issue with HIV-based plasmids is the repetitive LTR sequences bordering the internal HIV genes. These repetitive regions offer *E. coli* the opportunity to excise internal sequences while preserving resistance cassettes, for example, the beta lactamase ORF on the NL4-3 backbone. Engineered bacterial strains able to carry repetitive elements like LTRs have enabled easier cloning. New approaches like CRISPR/Cas9 have showed promise in the case of manipulating HIV *in vitro* an *in vivo* (Dash et al. 2019; Kaminski et al. 2016; Wang et al. 2016; Yin et al. 2017).

## References

Alexander, Thomas S. 2016. “Human Immunodeficiency Virus Diagnostic Testing: 30 Years of Evolution.” *Clinical and Vaccine Immunology* 23(4):249–53.

AP. 1986. “New Name Is Proposed For the Cause of AIDS.” *The New York Times*, May 1, 21.

Barré-Sinoussi, F., J. C. Chermann, F. Rey, M. T. Nugeyre, S. Chamaret, J. Gruest, C. Dauguet, C. Axler-Blin, F. Vézinet-Brun, C. Rouzioux, W. Rozenbaum, and L. Montagnier. 1983. “Isolation of a T-Lymphotropic Retrovirus from a Patient at Risk for Acquired Immune Deficiency Syndrome (AIDS).” *Science (New York, N.Y.)* 220(4599):868–71.

Cassan, Elodie, Anne-Muriel Arigon-Chifolleau, Jean-Michel Mesnard, Antoine Gross, and Olivier Gascuel. 2016. “Concomitant Emergence of the Antisense Protein Gene of HIV-1 and of the Pandemic.” *Proceedings of the National Academy of Sciences - PNAS* 113(41):11537–42.

CDC. 1981. “Pneumocystis Pneumonia--Los Angeles.” *MMWR. Morbidity and Mortality Weekly Report* 30(21):250–52.

Dash, Prasanta K., Rafal Kaminski, Ramona Bella, Hang Su, Saumi Mathews, Taha M. Ahooyi, Chen Chen, Pietro Mancuso, Rahsan Sariyer, Pasquale Ferrante, Martina Donadoni, Jake A. Robinson, Brady Sillman, Zhiyi Lin, James R. Hilaire, Mary Banoub, Monalisha Elango, Nagsen Gautam, R. Lee Mosley, Larisa Y. Poluektova, JoEllyn McMillan, Aditya N. Bade, Santhi Gorantla, Ilker K. Sariyer, Tricia H. Burdo, Won-Bin Young, Shohreh Amini, Jennifer Gordon, Jeffrey M. Jacobson, Benson Edagwa, Kamel Khalili, and Howard E. Gendelman. 2019. “Sequential LASER ART and CRISPR Treatments Eliminate HIV-1 in a Subset of Infected Humanized Mice.” *Nature Communications* 10(1):2753.

Dube MP. , Stein JH., Aberg JA. 2018. “Panel on Antiretroviral Guidelines for Adults and Adolescents. Guidelines for the Use of Antiretroviral Agents in Adults and Adolescents with HIV.” *Department of Health and Human Services* 40(Build 29393).

Gallo, R. C., P. S. Sarin, E. P. Gelmann, M. Robert-Guroff, E. Richardson, V. S. Kalyanaraman, D. Mann, G. D. Sidhu, R. E. Stahl, S. Zolla-Pazner, J. Leibowitch, and M. Popovic. 1983. “Isolation of Human T-Cell Leukemia Virus in Acquired Immune Deficiency Syndrome (AIDS).” *Science (New York, N.Y.)* 220(4599):865–67.

Gener, Alejandro R. 2021a. “Chapter 6 - Advancing HIV Informatics in the RNA Space: HIV MRNA Models.” Baylor College of Medicine.

Gener, Alejandro R. 2021b. “Chapter 7 - Advancing HIV Informatics in the RNA Space: HIV Virion MRNA.” Baylor College of Medicine.

Ghosn, Jade, Babafemi Taiwo, Soraya Seedat, Brigitte Autran, and Christine Katlama. 2018. “HIV (Seminar Lancet 2018).” *The Lancet* 392(10148):685–97.

Ginocchio, Christine C. 2001. “HIV-1 Viral Load Testing.” *Laboratory Medicine* 32(3):142–52.

Green, Michael R. and Joseph Sambrook. 2019. “Nested Polymerase Chain Reaction (PCR).” *Cold Spring Harbor Protocols* 2019(2):pdb.prot095182.

Hadzopoulou-Cladaras, M., B. K. Felber, C. Cladaras, A. Athanassopoulos, A. Tse, and G. N. Pavlakis. 1989. “The Rev (Trs/Art) Protein of Human Immunodeficiency Virus Type 1 Affects Viral MRNA and Protein Expression via a Cis-Acting Sequence in the Env Region.” *Journal of Virology* 63(3):1265–74.

Hahn, Beatrice H., George M. Shaw, Suresh K. Arya, Mikulas Popovic, Robert C. Gallo, and Flossie Wong-Staal. 1984. “Molecular Cloning and Characterization of the HTLV-III Virus Associated with AIDS.” *Nature* 312(5990):166–69.

Kaminski, Rafal, Yilan Chen, Tracy Fischer, Ellen Tedaldi, Alessandro Napoli, Yonggang Zhang, Jonathan Karn, Wenhui Hu, and Kamel Khalili. 2016. “Elimination of HIV-1 Genomes from Human T-Lymphoid Cells by CRISPR/Cas9 Gene Editing.” *Scientific Reports* 6(February):22555.

Levy, Jay A. 2007. *HIV and the Pathogenesis of AIDS*. 3rd ed. Washington: ASM Press.

Marschner, I. C., A. C. Collier, R. W. Coombs, R. T. D’Aquila, V. DeGruttola, M. A. Fischl, S. M. Hammer, M. D. Hughes, V. A. Johnson, D. A. Katzenstein, D. D. Richman, L. M. Smeaton, S. A. Spector, and M. S. Saag. 1998. “Use of Changes in Plasma Levels of Human Immunodeficiency Virus Type 1 RNA to Assess the Clinical Benefit of Antiretroviral Therapy.” *The Journal of Infectious Diseases* 177(1):40–47.

Menéndez-Arias, Luis. 2009. “Mutation Rates and Intrinsic Fidelity of Retroviral Reverse Transcriptases.” *Viruses* 1(3):1137–65.

Mermer, B., B. K. Felber, M. Campbell, and G. N. Pavlakis. 1990. “Identification of Trans-Dominant HIV-1 Rev Protein Mutants by Direct Transfer of Bacterially Produced Proteins into Human Cells.” *Nucleic Acids Research* 18(8):2037–44.

Metzker, Michael L., David P. Mindell, Xiao-Mei Liu, Roger G. Ptak, Richard A. Gibbs, and David M. Hillis. 2002. “Molecular Evidence of HIV-1 Transmission in a Criminal Case.” *Proceedings of the National Academy of Sciences* 99(22):14292 LP – 14297.

Murray, J. S., M. R. Elashoff, L. C. Iacono-Connors, T. A. Cvetkovich, and K. A. Struble. 1999. “The Use of Plasma HIV RNA as a Study Endpoint in Efficacy Trials of Antiretroviral Drugs.” *AIDS (London, England)* 13(7):797–804.

Ratner, L., W. Haseltine, R. Patarca, K. J. Livak, B. Starcich, S. F. Josephs, E. R. Doran, J. A. Rafalski, E. A. Whitehorn, and K. Baumeister. 1985. “Complete Nucleotide Sequence of the AIDS Virus, HTLV-III.” *Nature* 313(6000):277–84.

Saiki, R. K., D. H. Gelfand, S. Stoffel, S. J. Scharf, R. Higuchi, G. T. Horn, K. B. Mullis, and H. A. Erlich. 1988. “Primer-Directed Enzymatic Amplification of DNA with a Thermostable DNA Polymerase.” *Science* 239(4839):487 LP – 491.

Shendure, Jay, Shankar Balasubramanian, George M. Church, Walter Gilbert, Jane Rogers, Jeffery A. Schloss, and Robert H. Waterston. 2017. “DNA Sequencing at 40: Past, Present and Future.” *Nature* 550(7676):345–53.

Thiébaut, R., P. Morlat, H. Jacqmin-Gadda, D. Neau, P. Mercié, F. Dabis, and G. Chêne. 2000. “Clinical Progression of HIV-1 Infection According to the Viral Response during the First Year of Antiretroviral Treatment. Groupe d’Epidémiologie Du SIDA En Aquitaine (GECSA).” *AIDS (London, England)* 14(8):971–78.

Wang, Zhen, Qinghua Pan, Patrick Gendron, Weijun Zhu, Fei Guo, Shan Cen, Mark A. Wainberg, and Chen Liang. 2016. “CRISPR/Cas9-Derived Mutations Both Inhibit HIV-1 Replication and Accelerate Viral Escape.” *Cell Reports* 15(3):481–89.

Yin, Chaoran, Ting Zhang, Xiying Qu, Yonggang Zhang, Raj Putatunda, Xiao Xiao, Fang Li, Weidong Xiao, Huaqing Zhao, Shen Dai, Xuebin Qin, Xianming Mo, Won Bin Young, Kamel Khalili, and Wenhui Hu. 2017. “In Vivo Excision of HIV-1 Provirus by SaCas9 and Multiplex Single-Guide RNAs in Animal Models.” *Molecular Therapy* 25(5):1168–86.

Zucha, Daniel, Peter Androvic, Mikael Kubista, and Lukas Valihrach. 2020. “Performance Comparison of Reverse Transcriptases for Single-Cell Studies.” *Clinical Chemistry* 66(1):217–28.
