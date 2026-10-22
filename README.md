# Matematik – korta studieblad för årskurs 8

## Version 2

31 fristående A4-blad med korta förklaringar, en grå ruta för regel/formel, egna figurer, synliga mellanled, en första övning med stöd och arbetsytor anpassade till uppgiften. Alla övningar och facit hör ihop med version 2. Den tidigare versionen finns på grenen `v1`.

Materialet följer delområdena i innehållsförteckningen till *Modul matematik 8*. Det är eget studiematerial och inte utgivet av läromedelsförlaget. Det är avsett för grundläggande träning, utan fördjupningsuppgifter, och täcker inte ensamt alla betygskriterier.

## Skriv ut

- [Alla studieblad och facit i en PDF](output/pdf/Modul_8_studieblad.pdf)
- [Enbart facit, fem sidor](output/pdf/Modul_8_facit.pdf)
- [Separata PDF:er, samlade i en zip-fil](output/pdf/Modul_8_separata_blad.zip)
- [Alla separata studieblad och facit](output/pdf/Modul_8_separata_blad/)

Skriv ut i A4, enkelsidigt, faktisk storlek (100 %). Svartvitt går bra. I den samlade PDF:en är sidorna 1–31 studieblad och 32–36 facit. Rutorna är cirka 5 mm stora vid utskrift i 100 %. Varje blad är märkt `v2`.

## Pedagogiskt upplägg

Titel och kort sammanhang → förklaring, formel och exempel → fyra övningar → förklarad textuppgift → egen textövning → två punkter om vad eleven tränat på.

Varje liten uppgift har sin skrivyta intill sig. Textövningen står till vänster och en större arbetsyta till höger. Bladet om grafritning har ett koordinatsystem; sannolikhet och kombinatorik har friare punktade ytor för listor och träd. Se [designbeslut per blad](docs/pedagogik.md).

## Ändra och återskapa materialet

Python 3.10 eller senare. Matplotlib tillhandahåller typsnitten, så inga hårdkodade systemtypsnitt behövs.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/build.py
python scripts/split.py
```

I Windows aktiveras miljön med `.venv\Scripts\Activate.ps1` i PowerShell.

- `content/worksheets.json`: allt innehåll, alla övningar och aktuella svar.
- `scripts/build.py`: sidlayout, vektorformler, figurer och anpassade arbetsytor.
- `scripts/split.py`: separata PDF:er, facitsamling och zip-fil. Tar bort äldre genererade blad i samma utdatamapp.

Byggningen stoppar vid text som inte ryms i sin tilldelade yta. Efter innehållsändringar behöver även PDF-sidorna granskas visuellt.

## Blad och facit

- [1.1 addition-och-subtraktion-med-negativa-tal](output/pdf/Modul_8_separata_blad/1.1_addition-och-subtraktion-med-negativa-tal.pdf)
- [1.2 multiplikation-och-division-med-negativa-tal](output/pdf/Modul_8_separata_blad/1.2_multiplikation-och-division-med-negativa-tal.pdf)
- [1.3 blandade-raknesatt](output/pdf/Modul_8_separata_blad/1.3_blandade-raknesatt.pdf)
- [1.4 multiplikation-och-division-med-brak](output/pdf/Modul_8_separata_blad/1.4_multiplikation-och-division-med-brak.pdf)
- [1.5 potenser](output/pdf/Modul_8_separata_blad/1.5_potenser.pdf)
- [1.6 tiopotenser-och-grundpotensform](output/pdf/Modul_8_separata_blad/1.6_tiopotenser-och-grundpotensform.pdf)
- [2.1 forandringsfaktor](output/pdf/Modul_8_separata_blad/2.1_forandringsfaktor.pdf)
- [2.2 ranta](output/pdf/Modul_8_separata_blad/2.2_ranta.pdf)
- [2.3 procent-och-procentenheter](output/pdf/Modul_8_separata_blad/2.3_procent-och-procentenheter.pdf)
- [2.4 koordinatsystem-och-tolka-grafer](output/pdf/Modul_8_separata_blad/2.4_koordinatsystem-och-tolka-grafer.pdf)
- [2.5 proportionalitet](output/pdf/Modul_8_separata_blad/2.5_proportionalitet.pdf)
- [2.6 andra-linjara-funktioner](output/pdf/Modul_8_separata_blad/2.6_andra-linjara-funktioner.pdf)
- [2.7 rata-grafer](output/pdf/Modul_8_separata_blad/2.7_rata-grafer.pdf)
- [3.1 forenkla-parentesuttryck](output/pdf/Modul_8_separata_blad/3.1_forenkla-parentesuttryck.pdf)
- [3.2 multiplikation-med-parentesuttryck](output/pdf/Modul_8_separata_blad/3.2_multiplikation-med-parentesuttryck.pdf)
- [3.3 forenkla-och-berakna-vardet-av-ett-uttryck](output/pdf/Modul_8_separata_blad/3.3_forenkla-och-berakna-vardet-av-ett-uttryck.pdf)
- [3.4 formler](output/pdf/Modul_8_separata_blad/3.4_formler.pdf)
- [3.5 monster](output/pdf/Modul_8_separata_blad/3.5_monster.pdf)
- [3.6 ekvationer-med-parenteser](output/pdf/Modul_8_separata_blad/3.6_ekvationer-med-parenteser.pdf)
- [4.1 cirklar](output/pdf/Modul_8_separata_blad/4.1_cirklar.pdf)
- [4.2 cirkelbagar-och-cirkelsektorer](output/pdf/Modul_8_separata_blad/4.2_cirkelbagar-och-cirkelsektorer.pdf)
- [4.3 enheter-och-volym](output/pdf/Modul_8_separata_blad/4.3_enheter-och-volym.pdf)
- [4.4 prisma-och-cylinder](output/pdf/Modul_8_separata_blad/4.4_prisma-och-cylinder.pdf)
- [4.5 pyramider-och-koner](output/pdf/Modul_8_separata_blad/4.5_pyramider-och-koner.pdf)
- [4.6 pythagoras-sats](output/pdf/Modul_8_separata_blad/4.6_pythagoras-sats.pdf)
- [5.1 sannolikhet](output/pdf/Modul_8_separata_blad/5.1_sannolikhet.pdf)
- [5.2 sannolikhet-i-flera-steg](output/pdf/Modul_8_separata_blad/5.2_sannolikhet-i-flera-steg.pdf)
- [5.3 berakningar-med-sannolikheter](output/pdf/Modul_8_separata_blad/5.3_berakningar-med-sannolikheter.pdf)
- [5.4 sannolikhet-och-statistik](output/pdf/Modul_8_separata_blad/5.4_sannolikhet-och-statistik.pdf)
- [5.5 kombinatorik](output/pdf/Modul_8_separata_blad/5.5_kombinatorik.pdf)
- [5.6 lagesmatt-och-spridningsmatt](output/pdf/Modul_8_separata_blad/5.6_lagesmatt-och-spridningsmatt.pdf)
- [Facit kapitel 1](output/pdf/Modul_8_separata_blad/Facit_kapitel_1.pdf)
- [Facit kapitel 2](output/pdf/Modul_8_separata_blad/Facit_kapitel_2.pdf)
- [Facit kapitel 3](output/pdf/Modul_8_separata_blad/Facit_kapitel_3.pdf)
- [Facit kapitel 4](output/pdf/Modul_8_separata_blad/Facit_kapitel_4.pdf)
- [Facit kapitel 5](output/pdf/Modul_8_separata_blad/Facit_kapitel_5.pdf)
