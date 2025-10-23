# 💾 SD-Karten Backup Tool

Ein benutzerfreundliches Python-Tool zum Erstellen und Verkleinern von SD-Karten-Backups mit `dd` und `pishrink`.

## 📋 Inhaltsverzeichnis

- [Features](#-features)
- [Voraussetzungen](#-voraussetzungen)
- [Installation](#-installation)
- [Verwendung](#-verwendung)
- [Beispiele](#-beispiele)
- [Interaktive Geräteauswahl](#-interaktive-geräteauswahl)
- [Optionen](#-optionen)
- [Troubleshooting](#-troubleshooting)
- [Tipps & Tricks](#-tipps--tricks)
- [Technische Details](#-technische-details)

## ✨ Features

- 🔍 **Interaktive Laufwerksauswahl** - Zeigt alle verfügbaren Laufwerke mit Details
- 📊 **Echtzeit-Fortschrittsanzeige** - Live-Status während des Backup-Vorgangs
- 🗜️ **Automatische Verkleinerung** - Komprimiert das Backup mit pishrink
- 💾 **Wechseldatenträger-Erkennung** - Hebt SD-Karten und USB-Sticks hervor
- ⚠️ **Sicherheitsprüfungen** - Warnt vor gemounteten Partitionen
- 📈 **Statistiken** - Zeigt Größe, Dauer und Ersparnis an
- 🎯 **Benutzerfreundlich** - Klare Anweisungen und Fehlermeldungen
- 🔒 **Sicher** - Mehrfache Bestätigungen vor kritischen Aktionen

## 📦 Voraussetzungen

### System-Tools
```bash
# Auf Debian/Ubuntu/Raspberry Pi OS
sudo apt-get update
sudo apt-get install python3 lsblk coreutils util-linux
```

### Python
- Python 3.6 oder höher (normalerweise vorinstalliert)
- Keine zusätzlichen Python-Pakete erforderlich (nur stdlib)

### PiShrink (Optional, aber empfohlen)
```bash
wget https://raw.githubusercontent.com/Drewsif/PiShrink/master/pishrink.sh
chmod +x pishrink.sh
sudo mv pishrink.sh /usr/local/bin/
```

**Hinweis:** Das Skript funktioniert auch ohne PiShrink, überspringt dann aber die Verkleinerung.

## 🚀 Installation

### Schnellinstallation
```bash
# Skript herunterladen
wget https://raw.githubusercontent.com/DAI-SW/sd_backup.py

# Ausführbar machen
chmod +x sd_backup.py

# Optional: In PATH verschieben
sudo mv sd_backup.py /usr/local/bin/sd-backup
```

### Alternative: Direkt verwenden
```bash
# Einfach mit Python ausführen
python3 sd_backup.py
```

## 💻 Verwendung

### Einfachste Methode (Empfohlen)
Starte das Skript ohne Parameter für die interaktive Auswahl:

```bash
sudo python3 sd_backup.py
```

### Mit Parametern
```bash
# Grundlegende Verwendung
sudo python3 sd_backup.py /dev/sdb backup.img

# Automatischer Dateiname mit Zeitstempel
sudo python3 sd_backup.py /dev/sdb

# Ohne Verkleinerung
sudo python3 sd_backup.py /dev/sdb backup.img --no-shrink

# Mit anderer Block-Größe (schneller)
sudo python3 sd_backup.py /dev/sdb backup.img --block-size 8M
```

### Hilfe anzeigen
```bash
python3 sd_backup.py --help
```

## 📸 Beispiele

### Beispiel 1: Raspberry Pi SD-Karte sichern
```bash
# Interaktive Auswahl starten
sudo python3 sd_backup.py

# Ausgabe:
# ================================================================================
# 🔍 VERFÜGBARE LAUFWERKE
# ================================================================================
# 
# [1] 💿 sda
#     sda             238,5G  [Model: Samsung SSD 970]
#   ├─ sda1            512M  [FS: vfat, ⚠️  Gemountet: /boot/efi]
#   ├─ sda2          237,9G  [FS: ext4, ⚠️  Gemountet: /]
# 
# [2] 💾 sdb
#     sdb              31,9G  [Model: SD/MMC]
#   ├─ sdb1            256M  [Label: boot, FS: vfat]
#   ├─ sdb2           31,6G  [Label: rootfs, FS: ext4]
# 
# ➜ Wähle ein Laufwerk [1-2] oder 'q' zum Abbrechen: 2
```

### Beispiel 2: Direktes Backup mit Datum
```bash
sudo python3 sd_backup.py /dev/mmcblk0 raspi-$(date +%Y%m%d).img
```

### Beispiel 3: Schnelles Backup ohne Verkleinerung
```bash
sudo python3 sd_backup.py /dev/sdb quick-backup.img --no-shrink --block-size 8M
```

## 🎯 Interaktive Geräteauswahl

Die interaktive Auswahl zeigt dir:

| Symbol | Bedeutung |
|--------|-----------|
| 💾 | Wechseldatenträger (SD-Karte, USB-Stick) |
| 💿 | Festplatte oder SSD |
| ⚠️ | Partition ist gemountet |

### Angezeigte Informationen
- **Gerätename** (z.B. sdb, mmcblk0)
- **Größe** der Disk und Partitionen
- **Modellbezeichnung** (wenn verfügbar)
- **Labels** der Partitionen
- **Dateisystem-Typ** (ext4, vfat, etc.)
- **Mountpoints** (falls gemountet)

### Sicherheitsabfrage
Vor dem Start musst du **"JA"** (in Großbuchstaben) eingeben - ein zusätzlicher Schutz gegen versehentliches Überschreiben.

## ⚙️ Optionen

```
usage: sd_backup.py [-h] [--block-size BLOCK_SIZE] [--no-shrink] [device] [output]

Positionale Argumente:
  device                Quellgerät (z.B. /dev/sdb oder /dev/mmcblk0)
                        Wenn nicht angegeben: interaktive Auswahl
  output                Ausgabedatei (Standard: backup_GERÄT_DATUM_ZEIT.img)

Optionen:
  -h, --help            Zeigt diese Hilfe
  --block-size, -b      Block-Größe für dd (Standard: 4M)
                        Größere Werte = schneller (4M, 8M, 16M)
  --no-shrink           Keine Verkleinerung mit pishrink durchführen
```

## 🔧 Troubleshooting

### Problem: "pishrink.sh: /dev/loop0 is mounted" oder "target is busy"
```bash
# Das Skript verwendet jetzt automatisch zwei separate Dateien
# Original: backup_xxx.img
# Verkleinert: backup_xxx_shrunk.img

# Falls das Problem trotzdem auftritt, Loop-Devices manuell aufräumen:
sudo losetup -D

# Oder spezifisches Loop-Device unmounten:
sudo umount /dev/loop0
sudo losetup -d /dev/loop0
```

**Hinweis:** Das aktualisierte Skript vermeidet dieses Problem, indem es pishrink mit zwei verschiedenen Dateien aufruft (Quelle und Ziel), statt das Image "in-place" zu verkleinern.

### Problem: "Gerät ist beschäftigt"
```bash
# Alle Partitionen des Geräts unmounten
sudo umount /dev/sdb1
sudo umount /dev/sdb2

# Oder alle auf einmal
sudo umount /dev/sdb*
```

### Problem: "Permission denied"
```bash
# Skript immer mit sudo ausführen
sudo python3 sd_backup.py
```

### Problem: "pishrink.sh nicht gefunden"
```bash
# PiShrink installieren
wget https://raw.githubusercontent.com/Drewsif/PiShrink/master/pishrink.sh
chmod +x pishrink.sh
sudo mv pishrink.sh /usr/local/bin/

# Oder ohne Verkleinerung fortfahren
python3 sd_backup.py /dev/sdb backup.img --no-shrink
```

### Problem: Backup ist sehr langsam
```bash
# Größere Block-Größe verwenden
sudo python3 sd_backup.py /dev/sdb backup.img --block-size 16M

# Oder dd direkt mit optimierten Parametern
sudo dd if=/dev/sdb of=backup.img bs=16M status=progress conv=fsync
```

### Problem: "Kein Speicherplatz verfügbar"
```bash
# Verfügbaren Speicher prüfen
df -h

# Große Dateien finden und löschen
du -sh * | sort -h

# Altes Backup löschen
rm alte-backups/*.img
```

## 💡 Tipps & Tricks

### 1. Richtiges Laufwerk identifizieren

**VOR dem Einstecken der SD-Karte:**
```bash
lsblk
```

**NACH dem Einstecken der SD-Karte:**
```bash
lsblk
```
Das neue Gerät ist deine SD-Karte!

### 2. Backup auf USB-Festplatte speichern
```bash
# USB-Platte mounten
sudo mkdir -p /mnt/backup
sudo mount /dev/sdc1 /mnt/backup

# Backup erstellen
sudo python3 sd_backup.py /dev/sdb /mnt/backup/raspi-backup.img

# Danach unmounten
sudo umount /mnt/backup
```

### 3. Backup komprimieren (zusätzlich zu pishrink)
```bash
# Nach dem Backup mit gzip komprimieren
gzip backup_sdb_20251023_153045.img

# Oder während des Backups mit Pipe
sudo dd if=/dev/sdb bs=4M status=progress | gzip > backup.img.gz
```

### 4. Backup wiederherstellen
```bash
# Normale .img Datei
sudo dd if=backup.img of=/dev/sdb bs=4M status=progress conv=fsync

# Komprimierte .img.gz Datei
gunzip -c backup.img.gz | sudo dd of=/dev/sdb bs=4M status=progress
```

### 5. Backup-Integrität prüfen
```bash
# MD5-Checksumme erstellen
md5sum backup.img > backup.img.md5

# Später prüfen
md5sum -c backup.img.md5
```

### 6. Optimale Block-Größe finden
```bash
# Teste verschiedene Block-Größen (ohne tatsächlich zu schreiben)
for bs in 1M 2M 4M 8M 16M; do
    echo "Testing block size: $bs"
    sudo dd if=/dev/sdb of=/dev/null bs=$bs count=1000 2>&1 | grep copied
done
```

### 7. Regelmäßige Backups automatisieren
```bash
# Erstelle ein Cron-Job (wöchentlich)
sudo crontab -e

# Füge hinzu (jeden Sonntag um 2 Uhr morgens):
0 2 * * 0 /usr/bin/python3 /pfad/zu/sd_backup.py /dev/sdb /backups/weekly-$(date +\%Y\%m\%d).img
```

### 8. Schneller Backup mit dd_rescue
```bash
# Installation
sudo apt-get install ddrescue

# Verwendung (robuster bei fehlerhaften Sektoren)
sudo ddrescue -f /dev/sdb backup.img backup.log
```

## 🔬 Technische Details

### Was macht das Skript?

1. **Geräteauswahl**
   - Listet alle Block-Devices auf
   - Zeigt Details mit `lsblk`
   - Prüft auf Wechseldatenträger

2. **DD-Backup**
   - Verwendet `dd` mit `status=progress`
   - Parameter: `conv=fsync` für Datensicherheit
   - Blockweise Kopie aller Sektoren

3. **PiShrink-Verkleinerung**
   - Erstellt eine Kopie: `backup.img` → `backup_shrunk.img`
   - Verkleinert die Partition
   - Entfernt ungenutzten Speicherplatz
   - Macht das Image bootfähig auf kleineren SD-Karten
   - Fragt ob Original gelöscht werden soll

### Vergleich der Block-Größen

| Block-Größe | Geschwindigkeit | CPU-Last | Empfohlen für |
|-------------|-----------------|----------|---------------|
| 512K | Langsam | Niedrig | Alte/langsame Systeme |
| 1M | Mittel | Niedrig | Standard |
| 4M | Schnell | Mittel | **Empfohlen** (Standard) |
| 8M | Sehr schnell | Mittel | Große SD-Karten (>16GB) |
| 16M | Maximal | Hoch | Sehr große Karten (>64GB) |

### Geschwindigkeitsvergleich

**32GB SD-Karte Backup:**
- USB 2.0: ~20-30 Minuten (ca. 20 MB/s)
- USB 3.0: ~5-10 Minuten (ca. 80 MB/s)
- USB 3.1: ~3-5 Minuten (ca. 150 MB/s)

**Verkleinerung mit pishrink:**
- 32GB Image → ~8GB (je nach Datennutzung)
- Dauer: 2-5 Minuten
- Ersparnis: 60-75% typisch

### Sicherheitsaspekte

✅ **Was das Skript macht:**
- Liest nur vom Quellgerät (keine Schreibvorgänge)
- Fordert sudo-Rechte an (sichtbar für Benutzer)
- Multiple Bestätigungen vor Aktionen
- Zeigt alle betroffenen Geräte klar an

⚠️ **Was du beachten solltest:**
- Wähle IMMER das richtige Gerät aus
- Mounte gemountete Partitionen vorher aus
- Stelle sicher, dass genug Speicherplatz vorhanden ist
- Teste das Backup nach der Erstellung

## 📝 Häufige Anwendungsfälle

### Raspberry Pi Backup vor Update
```bash
sudo python3 sd_backup.py /dev/mmcblk0 raspi-before-update.img
```

### Mehrere SD-Karten klonen
```bash
# Master-Image erstellen
sudo python3 sd_backup.py /dev/sdb master.img

# Auf andere Karten schreiben
sudo dd if=master.img of=/dev/sdc bs=4M status=progress
sudo dd if=master.img of=/dev/sdd bs=4M status=progress
```

### Backup vor Experimenten
```bash
# Schnelles Backup ohne Verkleinerung
sudo python3 sd_backup.py /dev/sdb experiment-backup.img --no-shrink
```

## 📊 Ausgabe-Beispiel

```
================================================================================
🔧 SD-Karten Backup Tool
================================================================================

🔍 Erstelle Backup von /dev/sdb
📁 Zieldatei: backup_sdb_20251023_153045.img
💾 Gerätegröße: 31.91 GB

📋 Starte dd-Kopiervorgang...
============================================================
🔧 Befehl: sudo dd if=/dev/sdb of=backup_sdb_20251023_153045.img bs=4M status=progress conv=fsync

16106127360 bytes (16 GB, 15 GiB) copied, 450 s, 35.8 MB/s
31914983424 bytes (32 GB, 30 GiB) copied, 891.234 s, 35.8 MB/s

✅ Backup erfolgreich erstellt in 891.2 Sekunden
============================================================
📊 Backup-Größe: 31.91 GB


🔄 Starte Verkleinerung mit pishrink...
============================================================
✓ pishrink gefunden: /usr/local/bin/pishrink.sh
📊 Originalgröße: 14.56 GB
📁 Verkleinertes Image: backup_sdb_20251023_165059_shrunk.img
🔧 Befehl: sudo /usr/local/bin/pishrink.sh -v backup_sdb_20251023_165059.img backup_sdb_20251023_165059_shrunk.img

pishrink.sh v0.1.4
pishrink.sh: Copying backup_sdb_20251023_165059.img to backup_sdb_20251023_165059_shrunk.img... ...
pishrink.sh: Gathering data ...
pishrink.sh: Checking filesystem ...
rootfs: 142440/925696 files (0.1% non-contiguous), 1878525/3683840 blocks
resize2fs 1.47.0 (5-Feb-2023)
pishrink.sh: Shrinking filesystem ...
resize2fs 1.47.0 (5-Feb-2023)
Resizing the filesystem on /dev/loop1 to 2311739 (4k) blocks.
The filesystem on /dev/loop1 is now 2311739 (4k) blocks long.
pishrink.sh: Shrinking image ...
pishrink.sh: Shrunk backup_sdb_20251023_165059_shrunk.img from 15G to 9.4G ...

✅ Verkleinerung erfolgreich in 234.5 Sekunden
============================================================
📊 Original: 14.56 GB -> backup_sdb_20251023_165059.img
📊 Verkleinert: 9.40 GB -> backup_sdb_20251023_165059_shrunk.img
💾 Ersparnis: 5.16 GB (35.4%)
------------------------------------------------------------
❓ Original-Image löschen um Platz zu sparen? (j/n): j
✅ backup_sdb_20251023_165059.img gelöscht
📁 Verbleibendes Image: backup_sdb_20251023_165059_shrunk.img

============================================================
🎉 Fertig!
============================================================
```

## 🤝 Beitragen

Verbesserungsvorschläge und Bug-Reports sind willkommen!

## 📄 Lizenz

Dieses Skript ist Open Source und kann frei verwendet werden.

## ⚠️ Haftungsausschluss

Dieses Tool wurde mit Sorgfalt entwickelt, aber:
- **Erstelle immer Backups deiner Daten!**
- **Teste das Tool zuerst mit unwichtigen Daten!**
- **Der Autor übernimmt keine Haftung für Datenverlust!**
- **Verwende das Tool auf eigene Verantwortung!**

## 📚 Weiterführende Links

- [PiShrink GitHub](https://github.com/Drewsif/PiShrink)
- [dd Manual](https://man7.org/linux/man-pages/man1/dd.1.html)
- [Raspberry Pi Dokumentation](https://www.raspberrypi.org/documentation/)

---


