#!/usr/bin/env gaudirun.py 
# =============================================================================
# @file
#
# WG-production for
#
#  - B -> psi(') n*pi m*K     decays, 1<=(n+m)<= 6 
#  - B -> psi(') eta('),omega decays
#  - B -> psi(') K(K) eta('),omega decays
#  - B  -> psi C                                      (included into X )
#  - B+ -> psi (K*+ -> K+ pi0 ) for photon efficiency (included into X0) 
#  - B+ -> psi pp H
#
#  - Upsilon -> mumu
#  - chi_b   -> ( Upsilon gamma ) 
#
# Input :  DIMUON.DST
#
# Outputs :
#
#  - BandQ.PSIX.mdst
#  - BandQ.PSIX0.mdst
#  - BandQ.BOTTOM.mdst
#
# @author Vanya BELYAEV Ivan.Belyaev@itep.ru
# @date   2012-08-17
#
# @attention DataType and CondDB are not specified!
#
# For 2k+11-data:
#
# @code
#
#  gaudirun.py  $BANDQCONFIGROOT/scripts/BandQ.py $BANDQCONFIGROOT/scripts/DataType-2011.py  the_file_with_input_data.py
#
# @endcode
#
# For 2k+12-data:
#
# @code
# 
# gaudirun.py  $BANDQCONFIGROOT/scripts/BandQ.py $BANDQCONFIGROOT/scripts/DataType-2012.py  the_file_with_input_data.py
#
# @endcode
#
#                    $Revision: 150278 $
#  Last modification $Date: 2012-12-18 16:28:58 +0100 (Tue, 18 Dec 2012) $
#                 by $Author: ibelyaev $ 
# =============================================================================
"""

WG-production for

  - B -> psi(') n*pi m*K     decays, 1<=(n+m)<= 6 
  - B -> psi(') eta('),omega decays
  - B -> psi(') K(K) eta('),omega decays
  - B  -> psi C                                      (included into X )
  - B+ -> psi (K*+ -> K+ pi0 ) for photon efficiency (included into X0) 
  - B+ -> psi pp H

  - Upsilon -> mumu
  - chi_b   -> ( Upsilon gamma ) 

Input :  DIMUON.DST

Outputs :

  - BandQ.PSIX.mdst
  - BandQ.PSIX0.mdst
  - BandQ.UPSILON.mdst
    
Attention: DataType and CondDB are not specified!
> gaudirun.py  BandQ.py $BANDQCONFIGROOT/scripts/DataTypoe-2011.py   data.py
> gaudirun.py  BandQ.py $BANDQCONFIGROOT/scripts/DataTypoe-2012.py   data.py
   
"""
# =============================================================================
__author__   = "Vanya BELYAEV Ivan.Belyaev@itep.ru"
__date__     = "$Date: 2012-12-18 16:28:58 +0100 (Tue, 18 Dec 2012) $"
__version__  = "$Revision: 150278 $"
# =============================================================================
## logging
# =============================================================================
try : 
    from AnalysisPython.Logger import getLogger
    _name = __name__
    if 0 == _name.find ( '__'   ) : _name = 'WG/B&Q'
    logger = getLogger (  _name )
except:
    from Gaudi.Configuration import log as logger
    
# =============================================================================

## the_year = "2012"

# =============================================================================
# 1. construct the proper basic selections 
# =============================================================================
#
## location of dimuon candidates in TES:
#
from GaudiKernel.SystemOfUnits             import GeV, MeV, mm
from PhysSelPython.Wrappers import AutomaticData
#
jpsi_name = 'FullDSTDiMuonJpsi2MuMuDetachedLine'
psi2_name = 'FullDSTDiMuonPsi2MuMuDetachedLine'
upss_name = 'FullDSTDiMuonDiMuonHighMassLine'
#
jpsi  = AutomaticData ( '/Event/Dimuon/Phys/%s/Particles' % jpsi_name ) 
psi2s = AutomaticData ( '/Event/Dimuon/Phys/%s/Particles' % psi2_name )
upss  = AutomaticData ( '/Event/Dimuon/Phys/%s/Particles' % upss_name )
#
## merged selectoon for J/psi & psi'
#
from PhysSelPython.Wrappers import MergedSelection
psis = MergedSelection (
    'SelDetachedPsisForBandQ' ,  
    RequiredSelections = [ jpsi , psi2s ] 
    )

# =============================================================================
## Upsilon -> mumu, cuts by  Giulia Manca 
# ============================================================================= 
from GaudiConfUtils.ConfigurableGenerators import FilterDesktop
from PhysSelPython.Wrappers                import SimpleSelection
sel_ups = SimpleSelection (
    'Upsilon'     ,
    FilterDesktop , 
    [ upss ]      , 
    ## algorithm parameters 
    Code     = """
    ( M > 7 * GeV ) & 
    DECTREE   ('Meson -> mu+ mu-'  )                      &
    CHILDCUT( 1 , HASMUON & ISMUON )                      &
    CHILDCUT( 2 , HASMUON & ISMUON )                      & 
    ( MINTREE ( 'mu+' == ABSID , PT ) > 1 * GeV         ) &
    ( MAXTREE ( ISBASIC & HASTRACK , TRCHI2DOF ) < 4    ) & 
    ( MINTREE ( ISBASIC & HASTRACK , CLONEDIST ) > 5000 ) & 
    ( VFASPF  ( VPCHI2 ) > 0.5/100 ) 
    & ( abs ( BPV ( VZ    ) ) <  0.5 * meter     ) 
    & (       BPV ( vrho2 )   < ( 10 * mm ) ** 2 ) 
    """ ,
    ##
    Preambulo = [
    "vrho2 = VX**2 + VY**2"
    ] ,
    ## 
    ReFitPVs = True
    ##
    )

# =============================================================================
## chi_b -> Upsilon gamma 
# ============================================================================= 
from GaudiConfUtils.ConfigurableGenerators import CombineParticles 
from PhysSelPython.Wrappers                import SimpleSelection
from StandardParticles                     import StdLooseAllPhotons
sel1_chib = SimpleSelection (
    'PreSelChib'     ,
    CombineParticles , 
    [ sel_ups , StdLooseAllPhotons ] , 
    ## algorithm parameters 
    DecayDescriptor    = "chi_b1(1P) -> J/psi(1S) gamma" ,
    ## 
    DaughtersCuts      = {
    "gamma" : " ( 350 * MeV < PT ) & ( CL > 0.01 )  "
    } ,
    ## 
    CombinationCut     = """
    ( AM - AM1 ) < 2.1 * GeV 
    """ ,
    MotherCut          = " PALL" ,
    #
    ## we are dealing with photons!
    #
    ParticleCombiners  = { '' : 'LoKi::VertexFitter:PUBLIC' }
    # 
    )
#
## apply pi0-veto tagger
# 
from GaudiConfUtils.ConfigurableGenerators import Pi0Veto__Tagger
from PhysSelPython.Wrappers                import SimpleSelection
from GaudiKernel.SystemOfUnits             import MeV 
sel_chib = SimpleSelection (
    'ChiB'         ,
    Pi0Veto__Tagger , 
    [ sel1_chib ]   ,
    ## algorithm configuration 
    ExtraInfoIndex = 25001     , ## should be unique!
    MassWindow     = 20 * MeV  , ## cut on delta-mass 
    MassChi2       =       -1  , ## no cut for chi2(mass)
    )

# =============================================================================
from StrippingSelections.StrippingPsiXForBandQ import PsiX_BQ_Conf    as PsiX
from StrippingSelections.StrippingPsiX0        import PsiX0Conf       as PsiX0 
from StrippingSelections.StrippingPromptCharm  import StrippingPromptCharmConf as PC  

# =============================================================================
## redefine stripping configurations 
# ============================================================================= 

# =============================================================================
## redefine psi(') -> mu+ mu- to use "stripping versions" 
# =============================================================================

def _psi_ ( self ) :
    """
    psi(') -> mu+ mu- 
    """
    return psis

PsiX0 . psi = _psi_
PsiX  . psi = _psi_

logger.warning ( "Redefine PsiX .psi" )
logger.warning ( "Redefine PsiX0.psi" )


psix   = PsiX   ( 'PsiX'  , {} )
psix0  = PsiX0  ( 'PsiX0' , {} )

# ============================================================================-
## adjust vertex fitter
# ============================================================================-
for s in ( psix.psi_pi       () ,
           psix.psi_K        () ,
           #
           psix.psi_2pi      () ,
           psix.psi_2K       () ,
           psix.psi_2Kpi     () ,
           ## 
           psix.psi_3pi      () ,
           psix.psi_3K       () ,
           psix.psi_3Kpi     () ,
           ##
           psix.psi_4pi      () ,
           psix.psi_4Kpi     () ,
           psix.psi_4K       () ,
           ##
           psix.psi_5pi      () ,
           psix.psi_5K       () ,
           psix.psi_5Kpi     () ,
           ##
           psix.psi_6pi      () ,
           psix.psi_6Kpi     () ,
           ##
           psix.psi_7pi      () ,
           psix.psi_7Kpi     () ,
           ##
           # Lb 
           psix.psi_pK       () ,
           psix.psi_ppi      () ,
           psix.psi_pKpipi   () ,
           ##
           # 2protons 
           psix.psi_pp       () ,
           psix.psi_pppi     () ,
           psix.psi_ppK      () ,
           psix.psi_pppipi   () ,
           psix.psi_ppKpipi  () ,
           psix.psi_pppipipi () ,
           ##
           ) : 
           
    a = s.algorithm ()
    a.ParticleCombiners = { '' : 'LoKi::VertexFitter:PUBLIC' }
    #
    a.MaxCandidates          = 2000
    a.StopAtMaxCandidates    = True 
    a.StopIncidentType       = 'ExceedsCombinatoricsLimit'
    # 

# ==============================================================================
## B+X-selections 
# ==============================================================================
beauty  = psix.beauty    ()
pc      = PC ('PromptCharm', {
    'pT(D0)'           :  0.95 * GeV ,    ## pt-cut for  prompt   D0
    'pT(D+)'           :  0.95 * GeV ,    ## pt-cut for  prompt   D+
    'pT(Ds+)'          :  0.95 * GeV ,    ## pt-cut for  prompt   Ds+
    'pT(Lc+)'          :  0.95 * GeV ,    ## pt-cut for  prompt   Lc+
    } ) 
prompt  = pc.PromptCharm () 
w       = pc.W           ()
dimu_pr = pc.DiMuon      () 

##

# ==============================================================================
## Xi_c+ -> p K- pi+ 
# ==============================================================================
from GaudiConfUtils.ConfigurableGenerators import DaVinci__N3BodyDecays
from PhysSelPython.Wrappers                import SimpleSelection
xic_sel = SimpleSelection (
    'SelXic2pKpi'           ,
    DaVinci__N3BodyDecays   , 
    [ pc.protons() , pc.kaons() , pc.pions () ] , 
    #
    ## decay descriptor 
    DecayDescriptor = " [ Lambda_c+ -> p+  K-  pi+ ]cc" ,
    ##
    Combination12Cut  = """
    ( AM < 2.6 * GeV      ) &
    ( ACHI2DOCA(1,2) < 16 ) 
    """ ,
    ## 
    CombinationCut    = """
    ( ( ADAMASS ( 'Lambda_c+' ) < 110 * MeV ) 
    | ( ADAMASS ( 'Xi_c+'     ) < 110 * MeV ) ) &
    ( APT            > 450 * MeV ) & 
    ( ACHI2DOCA(1,3) < 16        ) &
    ( ACHI2DOCA(2,2) < 16        ) 
    """ , 
    ##
    MotherCut      = """
    (  VFASPF(VCHI2) < 25                    ) &
    ( PT             > 500 * MeV             ) &
    ( ( ADMASS ( 'Lambda_c+' ) < 105 * MeV ) 
    | ( ADMASS ( 'Xi_c+'     ) < 105 * MeV ) ) 
    """ , 
    ParticleCombiners = { '' : 'LoKi::VertexFitter:PUBLIC' } 
    )

# ==============================================================================
## XXX -> J/psi Xi_c+ 
# ==============================================================================
from GaudiConfUtils.ConfigurableGenerators import CombineParticles 
from PhysSelPython.Wrappers                import SimpleSelection
xibc_sel = SimpleSelection (
    'SelXibc2psiXic'          ,
    CombineParticles          ,
    [ psix.psi () , xic_sel ] ,
    ## algorithm configuration 
    DecayDescriptors = [
    " [ Xi_bc+ -> J/psi(1S) Xi_c+     ]cc" ,
    " [ Xi_bc+ -> J/psi(1S) Lambda_c+ ]cc"
    ] ,
    # 
    CombinationCut    = " in_range ( 4 * GeV , AM , 20 * GeV ) ", 
    MotherCut         = """
    ( VFASPF ( VCHI2PDOF ) < 4000 ) 
    """ , 
    ParticleCombiners = { '' : 'LoKi::VertexFitter:PUBLIC' } 
    )
# ==============================================================================
## B&W 
# ==============================================================================
from GaudiConfUtils.ConfigurableGenerators import CombineParticles
from PhysSelPython.Wrappers                import SimpleSelection
bw_sel = SimpleSelection (
    'SelB&W'                    ,
    CombineParticles            ,
    [ pc.W()  , psix.beauty() ] ,
    # 
    ## the decays to be reconstructed
    DecayDescriptors = [
    #
    # charm-anti-charm
    #
    " [ chi_b0(2P) -> B0        mu+ ]cc " ,
    " [ chi_b0(2P) -> B~0       mu+ ]cc " ,
    " [ chi_b0(2P) -> B+        mu+ ]cc " ,
    " [ chi_b0(2P) -> B-        mu+ ]cc " ,
    " [ chi_b0(2P) -> B_s0      mu+ ]cc " ,
    " [ chi_b0(2P) -> B_s0      mu- ]cc " ,
    ] ,
    ##
    ## combination cut : accept all
    CombinationCut = " AALL " ,
    ##      mother cut : accept all
    MotherCut      = "  ALL " , 
    #
    ## make the selection faster
    #
    ParticleCombiners = { '' : 'LoKi::VertexFitter:PUBLIC' } 
    #
    )

# ==============================================================================
## B&B
# ==============================================================================
from GaudiConfUtils.ConfigurableGenerators import CombineParticles
from PhysSelPython.Wrappers                import SimpleSelection
bb_sel = SimpleSelection (
    ##
    'SelB&B'          ,
    CombineParticles  , 
    [ psix.beauty() ] ,
    # 
    ## the decays to be reconstructed
    DecayDescriptors = [
    #
    # beauty+beauty
    #
    "   chi_b0(2P) -> B0        B~0       " ,
    "   chi_b0(2P) -> B+        B-        " ,
    "   chi_b0(2P) -> B_s0      B_s0      " ,
    #
    " [ chi_b0(2P) -> B0        B0    ]cc " ,
    " [ chi_b0(2P) -> B0        B+    ]cc " ,
    " [ chi_b0(2P) -> B0        B_s0  ]cc " ,
    # 
    " [ chi_b0(2P) -> B0        B-    ]cc " ,
    " [ chi_b0(2P) -> B0        B_s~0 ]cc " ,
    #
    " [ chi_b0(2P) -> B+        B+    ]cc " ,
    " [ chi_b0(2P) -> B+        B_s0  ]cc " ,
    " [ chi_b0(2P) -> B+        B_s~0 ]cc " ,
    #
    ] ,
    #
    ## combination cut : accept all
    #
    CombinationCut = " AALL " ,
    #
    ##      mother cut : accept all
    #
    MotherCut      = "  ALL " , 
    #
    ## make the selection faster
    #
    ParticleCombiners = { '' : 'LoKi::VertexFitter:PUBLIC' } 
    #
    )


# ==============================================================================
## B&C
# ==============================================================================
from GaudiConfUtils.ConfigurableGenerators import CombineParticles
from PhysSelPython.Wrappers                import SimpleSelection
bc_sel = SimpleSelection (
    'SelB&C'          ,
    CombineParticles  , 
    [ psix . beauty() , pc . PromptCharm() ] , 
    # 
    ## the decays to be reconstructed
    DecayDescriptors = [
    #
    # beauty + charm
    #
    " [ chi_b0(2P) -> B0        D0         ]cc " ,
    " [ chi_b0(2P) -> B0        D+         ]cc " ,
    " [ chi_b0(2P) -> B0        D*(2010)+  ]cc " ,
    " [ chi_b0(2P) -> B0        D_s+       ]cc " ,
    " [ chi_b0(2P) -> B0        Lambda_c+  ]cc " ,
    #
    " [ chi_b0(2P) -> B0        D~0        ]cc " ,
    " [ chi_b0(2P) -> B0        D-         ]cc " ,
    " [ chi_b0(2P) -> B0        D*(2010)-  ]cc " ,
    " [ chi_b0(2P) -> B0        D_s-       ]cc " ,
    " [ chi_b0(2P) -> B0        Lambda_c~- ]cc " ,
    #
    " [ chi_b0(2P) -> B+        D0         ]cc " ,
    " [ chi_b0(2P) -> B+        D+         ]cc " ,
    " [ chi_b0(2P) -> B+        D*(2010)+  ]cc " ,
    " [ chi_b0(2P) -> B+        D_s+       ]cc " ,
    " [ chi_b0(2P) -> B+        Lambda_c+  ]cc " ,
    #
    " [ chi_b0(2P) -> B+        D~0        ]cc " ,
    " [ chi_b0(2P) -> B+        D-         ]cc " ,
    " [ chi_b0(2P) -> B+        D*(2010)-  ]cc " ,
    " [ chi_b0(2P) -> B+        D_s-       ]cc " ,
    " [ chi_b0(2P) -> B+        Lambda_c~- ]cc " ,
    #
    #
    " [ chi_b0(2P) -> B_s0      D0         ]cc " ,
    " [ chi_b0(2P) -> B_s0      D+         ]cc " ,
    " [ chi_b0(2P) -> B_s0      D*(2010)+  ]cc " ,
    " [ chi_b0(2P) -> B_s0      D_s+       ]cc " ,
    " [ chi_b0(2P) -> B_s0      Lambda_c+  ]cc " ,
    #
    " [ chi_b0(2P) -> B_s0      D~0        ]cc " ,
    " [ chi_b0(2P) -> B_s0      D-         ]cc " ,
    " [ chi_b0(2P) -> B_s0      D*(2010)-  ]cc " ,
    " [ chi_b0(2P) -> B_s0      D_s-       ]cc " ,
    " [ chi_b0(2P) -> B_s0      Lambda_c~- ]cc " ,
    #
    ] ,
    ## combination cut : accept all
    CombinationCut = " AALL " ,
    ##      mother cut : accept all
    MotherCut      = "  ALL " , 
    #
    ## make the selection faster
    #
    ParticleCombiners = { '' : 'LoKi::VertexFitter:PUBLIC' } 
    #
    )


# ==============================================================================
## B&2mu
# ==============================================================================
from GaudiConfUtils.ConfigurableGenerators import CombineParticles
from PhysSelPython.Wrappers                import SimpleSelection
bm_sel = SimpleSelection (
    'SelB&2Mu'         ,
    CombineParticles   , 
    [ psix . beauty () , pc . DiMuon () ] ,
    #
    ## the decays to be reconstructed
    DecayDescriptors = [
    #
    # beauty+2mu
    #
    " [ chi_b0(2P) -> B0        J/psi(1S)  ]cc " ,
    " [ chi_b0(2P) -> B+        J/psi(1S)  ]cc " ,
    "   chi_b0(2P) -> B_s0      J/psi(1S)      " ,
    #
    ] ,
    ##
    ## combination cut : accept all
    CombinationCut = " AALL " ,
    ##      mother cut : accept all
    MotherCut      = "  ALL " , 
    #
    ## make the selection faster
    #
    ParticleCombiners = { '' : 'LoKi::VertexFitter:PUBLIC' } 
    #
    )

# =============================================================================
## Y + prompt charm 
# =============================================================================
from GaudiConfUtils.ConfigurableGenerators import CombineParticles 
from PhysSelPython.Wrappers                import SimpleSelection
sel_Ycharm = SimpleSelection (
    'Y&Charm'        ,
    CombineParticles , 
    [ sel_ups        , pc.PromptCharm() ] , 
    ## algorithm parameters 
    DecayDescriptors    = [
    "[ chi_b1(1P) -> J/psi(1S) D0        ]cc" ,
    "[ chi_b1(1P) -> J/psi(1S) D+        ]cc" ,
    "[ chi_b1(1P) -> J/psi(1S) D*(2010)+ ]cc" ,
    "[ chi_b1(1P) -> J/psi(1S) D_s+      ]cc" ,
    "[ chi_b1(1P) -> J/psi(1S) Lambda_c+ ]cc" ,
    ] , 
    CombinationCut     = " AALL " ,
    MotherCut          = "  ALL " , 
    ParticleCombiners  = { '' : 'LoKi::VertexFitter:PUBLIC' }
    # 
    )


from PhysSelPython.Wrappers import MultiSelectionSequence
from PhysSelPython.Wrappers import      SelectionSequence

# =============================================================================
## PSIX0 stream 
# =============================================================================
psi_x0 = MultiSelectionSequence (
    "PSIX0",
    Sequences = [
    #
    SelectionSequence ( 'ETA'           , psix0 . b2eta       () ) ,
    SelectionSequence ( 'ETAPRIME'      , psix0 . b2etap      () ) ,
    SelectionSequence ( 'OMEGA'         , psix0 . b2omega     () ) ,
    #
    SelectionSequence ( 'KETA'          , psix0 . b2Keta      () ) ,
    SelectionSequence ( 'KETAPRIME'     , psix0 . b2Ketap     () ) ,
    SelectionSequence ( 'KOMEGA'        , psix0 . b2Komega    () ) ,
    #
    SelectionSequence ( 'KKETA'         , psix0 . b2KKeta     () ) ,
    SelectionSequence ( 'KKETAPRIME'    , psix0 . b2KKetap    () ) ,
    SelectionSequence ( 'KKOMEGA'       , psix0 . b2KKomega   () ) ,
    #
    SelectionSequence ( 'PIETA'         , psix0 . b2pieta     () ) ,
    SelectionSequence ( 'PIETAPRIME'    , psix0 . b2pietap    () ) ,
    SelectionSequence ( 'PIOMEGA'       , psix0 . b2piomega   () ) ,
    #
    SelectionSequence ( 'PIPIETA'       , psix0 . b2pipieta   () ) ,
    SelectionSequence ( 'PIPIETAPRIME'  , psix0 . b2pipietap  () ) ,
    SelectionSequence ( 'PIPIOMEGA'     , psix0 . b2pipiomega () ) ,
    #
    SelectionSequence ( 'KPIETA'        , psix0 . b2Kpieta    () ) ,
    SelectionSequence ( 'KPIETAPRIME'   , psix0 . b2Kpietap   () ) ,
    SelectionSequence ( 'KPIOMEGA'      , psix0 . b2Kpiomega  () ) ,
    #
    ] 
    )

# =============================================================================
## PSIX stream 
# =============================================================================
psi_x = MultiSelectionSequence (
    "PSIX"      ,
    Sequences = [
    #
    SelectionSequence ( 'B2PsiK'    , psix . psi_K    () ) ,
    SelectionSequence ( 'B2PsiPi'   , psix . psi_pi   () ) ,
    #
    SelectionSequence ( 'B2Psi2K'   , psix . psi_2K   () ) ,
    SelectionSequence ( 'B2Psi2KPi' , psix . psi_2Kpi () ) ,
    SelectionSequence ( 'B2Psi2Pi'  , psix . psi_2pi  () ) ,
    #
    SelectionSequence ( 'B2Psi3K'   , psix . psi_3K   () ) ,
    SelectionSequence ( 'B2Psi3KPi' , psix . psi_3Kpi () ) ,
    SelectionSequence ( 'B2Psi3Pi'  , psix . psi_3pi  () ) ,
    #
    SelectionSequence ( 'B2Psi4K'   , psix . psi_4K   () ) ,
    SelectionSequence ( 'B2Psi4KPi' , psix . psi_4Kpi () ) ,
    SelectionSequence ( 'B2Psi4Pi'  , psix . psi_4pi  () ) ,
    #
    SelectionSequence ( 'B2Psi5K'   , psix . psi_5K   () ) ,
    SelectionSequence ( 'B2Psi5KPi' , psix . psi_5Kpi () ) ,
    SelectionSequence ( 'B2Psi5Pi'  , psix . psi_5pi  () ) ,
    #
    SelectionSequence ( 'B2Psi6KPi' , psix . psi_6Kpi () ) ,
    SelectionSequence ( 'B2Psi6Pi'  , psix . psi_6pi  () ) ,
    #
    SelectionSequence ( 'B2Psi7KPi' , psix . psi_7Kpi () ) ,
    SelectionSequence ( 'B2Psi7Pi'  , psix . psi_7pi  () ) ,
    #
    ## Lb
    #
    SelectionSequence ( 'Lb2PSIPK'      , psix . psi_pK      () ) ,
    SelectionSequence ( 'Lb2PSIPPi'     , psix . psi_ppi     () ) ,
    SelectionSequence ( 'Lb2PSIPKPiPi'  , psix . psi_pKpipi  () ) ,
    SelectionSequence ( 'Lb2PSIPPiPiPi' , psix . psi_ppipipi () ) ,
    #
    # 2 protons
    #
    SelectionSequence ( 'B2PSIPP'       , psix . psi_pp       () ) ,
    SelectionSequence ( 'B2PSIPPPi'     , psix . psi_pppi     () ) ,
    SelectionSequence ( 'B2PSIPPK'      , psix . psi_ppK      () ) ,
    SelectionSequence ( 'B2PSIPPPiPi'   , psix . psi_pppipi   () ) ,
    SelectionSequence ( 'B2PSIPPKPiPi'  , psix . psi_ppKpipi  () ) ,
    SelectionSequence ( 'B2PSIPPPiPiPi' , psix . psi_pppipipi () ) ,
    #
    ## B + X
    #
    SelectionSequence ( 'B&B'           , bb_sel  )  ,    
    SelectionSequence ( 'B&C'           , bc_sel  )  ,    
    SelectionSequence ( 'B&2Mu'         , bm_sel  )  ,    
    SelectionSequence ( 'B&W'           , bw_sel  )  ,    
    #
    ## Xi_bc+                     ## new 
    #
    SelectionSequence ( 'XIBC'            , xibc_sel )  ,    
    #
    ##  Bc -> J/psi rho+          ## new 
    # 
    SelectionSequence ( 'BC2RHO'          , psix0 . bc2rho     () ) ,
    # 
    ## for the photon efficiency: ## new 
    #
    SelectionSequence ( 'KSTARPLUS'       , psix0 . bu2Kstar   () ) ,
    SelectionSequence ( 'KSTARPLUSMERGED' , psix0 . bu2KstarM  () ) , 
    #
    ## channels with chic
    # 
    SelectionSequence ( 'B2CHICK'     , psix0 . b2chicK     () ) ,
    SelectionSequence ( 'B2CHICKK'    , psix0 . b2chicKK    () ) ,
    SelectionSequence ( 'B2CHICKPi'   , psix0 . b2chicKpi   () ) ,
    SelectionSequence ( 'B2CHICKPiPi' , psix0 . b2chicKpipi () ) ,
    SelectionSequence ( 'B2CHICPiPi'  , psix0 . b2chicpipi  () ) ,
    #
    SelectionSequence ( 'BC2CHICPi'   , psix0 . bc2chicpi    () ) ,
    SelectionSequence ( 'Lb2CHICPi'   , psix0 . lb2chicpK    () ) ,
    ]
    )


# =============================================================================
## UPSILON stream 
# =============================================================================
bottom = MultiSelectionSequence (
    'BOTTOM' ,
    Sequences = [
    SelectionSequence ( 'Ups' , sel_ups    ) ,
    ## SelectionSequence ( 'Chib', sel_chib   ) ,
    SelectionSequence ( 'Y&C' , sel_Ycharm ) 
    ]
    )

# =============================================================================
## micro-DST writer
# =============================================================================
from DSTWriters.Configuration import ( SelDSTWriter            ,
                                       stripMicroDSTStreamConf ,
                                       stripMicroDSTElements   )

# Configuration of SelDSTWriter
SelDSTWriterConf     = { 'default' : stripMicroDSTStreamConf ( pack = False ) }
SelDSTWriterElements = { 'default' : stripMicroDSTElements   ( pack = False , refit = True ) }

uDstWriter = SelDSTWriter(
    "MyDSTWriter"                          ,
    StreamConf         =  SelDSTWriterConf      ,
    MicroDSTElements   =  SelDSTWriterElements  ,
    OutputFileSuffix   = 'BandQ'                ,  ## output PRE-fix! 
    SelectionSequences = [ 
                           psi_x0 ,
                           ]
    )

#
## Read only fired events to speed up
#
from PhysConf.Filters import LoKi_Filters
fltrs = LoKi_Filters (
    STRIP_Code = """
    HLT_PASS_RE ( 'Stripping.*DiMuonJpsi2MuMuDetached.*' ) |
    HLT_PASS_RE ( 'Stripping.*DiMuonPsi2MuMuDetached.*'  ) |
    HLT_PASS_RE ( 'Stripping.*DiMuonDiMuonHighMass.*'    )     
    """ 
    )

# 
## protection against ``corrupted'' Stripping 17b DIMUON.DST
#  obsolete? 
#  also add protection against very busy events
fltrs_0 = LoKi_Filters (
    VOID_Code  = """
    ( EXISTS     ( '/Event/DAQ/RawEvent' ) | EXISTS ( '/Event/Trigger/RawEvent' ) ) 
    & EXISTS     ( '/Event/Strip/Phys/DecReports') &
    ( RECSUMMARY (  0 , -1 )                                > 0.5 ) & 
    ( RECSUMMARY ( 10 , -1 )                                < 500 ) & 
    ( RECSUMMARY ( 13 , -1 )                                < 500 ) & 
    ( CONTAINS   ( '/Event/Phys/StdLooseKaons/Particles' )  < 250 ) & 
    ( CONTAINS   ( '/Event/Phys/StdLoosePions/Particles' )  < 250 ) 
    """,
    VOID_Preambulo = ["from LoKiCore.functions import * "]
    )

# ==============================================================================
# The last step: DaVinci & DB 
# ==============================================================================

from Configurables import DaVinci 
davinci = DaVinci ( 
    #
    ## DataType        = the_year ,                ## ATTENTION !!
    #
    EventPreFilters = fltrs_0.filters ('Filters0') + fltrs.filters ('Filters') , 
    InputType       = "DST"    , 
    EvtMax          =    -1    ,  
    PrintFreq       =  1000    ,
    Lumi            =  True    ,  
    )

davinci.appendToMainSequence( [ uDstWriter.sequence() ] )

## from Configurables import CondDB
## CondDB ( LatestGlobalTagByDataType = the_year )  ## ATTENTION !!
    
# =============================================================================
if '__main__' == __name__ :
    
    print 100*'*'
    print __doc__
    print 100*'*'
    print ' Author  : %s ' % __author__
    print ' Version : %s ' % __version__ 
    print ' Date    : %s ' % __date__
    print 100*'*'


# =============================================================================
# The END 
# =============================================================================

