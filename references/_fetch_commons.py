import sys, urllib.parse
sys.path.insert(0, "scripts"); import ref_hunt as r
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
r.PACE = 9.0
TT = ["TT-30 Tokarev 001.jpg", "TT-30 Tokarev 002.jpg", "Tokarev TT-33-IMG 6551-white.jpg", "Tokarev TT-33-IMG 6553-white.jpg",
      "Tokarev pistol TT at Tula State Museum of Weapons.jpg", "TT 33.jpg", "TT 1.jpg", "TT 2.jpg", "TT 3.jpg", "TT33.JPG",
      "TT-33.JPG", "TT-33 2.JPG", "TT 33 Pistol.jpg", "Soviet TT M1933 automatic pistol.jpg", "TT33 noBG.jpg",
      "TT rozłożony.jpg", "Magazynek TT.jpg", "TT zadergka.jpg", "Tokarev TT33 (6825679152).jpg",
      "TT pistol 1933 WW2 USSR 2021.jpg", "1953 TTC.jpg", "Pistol, automatic (AM 1985.370-16).jpg",
      "Пистолет ТТ - Оружейная кузница России 01.jpg", "Tula State Museum of Weapons (79-12).jpg",
      "Tula State Museum of Weapons (79-13).jpg", "Филиал ЦВММ «Дорога жизни», ТТ.jpg",
      "KGB Cells Museum (Tartu, Estonia).04.jpg", "TTBell2020.jpg", "PW-33 1.jpg"]
PPSH = ["PPSh 41-07450-IMG 7476-white.jpg", "Soviet machine gun PPSh-41 right side.jpg", "PPSh-41 from soviet.jpg",
        "PPSh-41 with box magazine 1942 001.jpg", "Soviet PPSH-41 SMG.jpg", "Soviet PPSH-41 sub-machine gun.JPEG",
        "PPSH Submachine Gun.jpg", "PPS-41 submachine gun.jpg", "Пистолет-пулемет системы Шпагина обр. 1941.jpg",
        "PPSh machine gun (DOSAAF Museum in Minsk) 1.jpg", "PPSh machine gun (DOSAAF Museum in Minsk) 2.jpg",
        "PPSh-41 Penry Museum.JPG", "PPsh-41 at the National Museum of Scotland.jpg", "Ppsh 41 berlin.jpg", "MP41(r).jpg",
        "Diappsh41.png", '"Burp Gun" (10470348934).jpg', "PPSz-41 - Muzeum w Nieborowie.jpg", "DA-SD-04-13607.jpg",
        "Mitragliatore sovietico.JPG", "M1 Garand PPsh-41 Sturmgewehr 44.jpg",
        "Suomi ja PPSH-41 Kasarminkankaan vanhassa paloasemassa.JPG"] + [
        "Muzeum československých legií - Sokolská 33, 120 00 Nové Město 20240921 %s.jpg" % n
        for n in ("094227", "094231", "094236", "094240", "094245", "094254")]
for gun, names in (("tt", TT), ("ppsh41", PPSH)):
    items = []
    for n in names:
        q = urllib.parse.quote(n.replace(" ", "_"))
        items.append((n, "https://commons.wikimedia.org/wiki/File:" + q,
                      "https://commons.wikimedia.org/wiki/Special:FilePath/%s?width=1600" % q,
                      "commons:" + n, "see file page"))
    print(gun, "saved", r.save(gun, "commons", items))
    r.sheet(gun, "commons")
