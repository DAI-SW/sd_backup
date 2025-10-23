#!/usr/bin/env python3
"""
SD-Karten Backup Tool mit dd und pishrink
Erstellt ein komplettes Backup einer SD-Karte und verkleinert es anschließend
"""

import subprocess
import sys
import os
import time
import json
from pathlib import Path
import argparse
from datetime import datetime


class SDBackup:
    def __init__(self, source_device, output_file, block_size="4M"):
        self.source_device = source_device
        self.output_file = output_file
        self.block_size = block_size


def list_block_devices():
    """Listet alle verfügbaren Block-Devices mit Details auf"""
    try:
        # lsblk mit JSON-Output für einfaches Parsing
        result = subprocess.run(
            ['lsblk', '-J', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT,LABEL,FSTYPE,MODEL'],
            capture_output=True,
            text=True,
            check=True
        )
        
        devices_data = json.loads(result.stdout)
        return devices_data.get('blockdevices', [])
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler beim Auflisten der Geräte: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Fehler beim Parsen der Geräteinformationen: {e}")
        return []


def is_removable(device_name):
    """Prüft ob ein Gerät als removable markiert ist"""
    try:
        removable_path = f'/sys/block/{device_name}/removable'
        if os.path.exists(removable_path):
            with open(removable_path, 'r') as f:
                return f.read().strip() == '1'
    except:
        pass
    return False


def format_device_info(device, indent=0):
    """Formatiert Geräteinformationen für die Anzeige"""
    prefix = "  " * indent
    name = device.get('name', 'N/A')
    full_path = f"/dev/{name}"
    size = device.get('size', 'N/A')
    dev_type = device.get('type', 'N/A')
    mountpoint = device.get('mountpoint', '')
    label = device.get('label', '')
    fstype = device.get('fstype', '')
    model = device.get('model', '')
    
    # Basis-Info
    info = f"{prefix}├─ {name:15} {size:>10}"
    
    # Zusätzliche Informationen
    details = []
    if model and model.strip():
        details.append(f"Model: {model.strip()}")
    if label:
        details.append(f"Label: {label}")
    if fstype:
        details.append(f"FS: {fstype}")
    if mountpoint:
        details.append(f"⚠️  Gemountet: {mountpoint}")
    
    if details:
        info += f"  [{', '.join(details)}]"
    
    return info, full_path, name


def select_device_interactive():
    """Interaktive Geräteauswahl mit Warnung vor falscher Auswahl"""
    print("\n" + "=" * 80)
    print("🔍 VERFÜGBARE LAUFWERKE")
    print("=" * 80)
    
    devices = list_block_devices()
    
    if not devices:
        print("❌ Keine Geräte gefunden!")
        return None
    
    # Liste für auswählbare Geräte (nur Disks, keine Partitionen)
    selectable_devices = []
    device_index = 1
    
    for device in devices:
        dev_type = device.get('type', '')
        name = device.get('name', '')
        
        # Nur Disks anzeigen (keine Partitionen, loops, etc.)
        if dev_type == 'disk':
            # Prüfen ob removable
            removable = is_removable(name)
            removable_icon = "💾" if removable else "💿"
            
            print(f"\n[{device_index}] {removable_icon} {name}")
            info, full_path, _ = format_device_info(device, indent=0)
            print(info.replace('├─', '   '))
            
            # Partitionen anzeigen
            children = device.get('children', [])
            for child in children:
                child_info, _, _ = format_device_info(child, indent=1)
                print(child_info)
            
            selectable_devices.append({
                'number': device_index,
                'path': full_path,
                'name': name,
                'device': device,
                'removable': removable
            })
            device_index += 1
    
    if not selectable_devices:
        print("\n❌ Keine geeigneten Laufwerke gefunden!")
        return None
    
    print("\n" + "=" * 80)
    print("💾 = Wechseldatenträger (SD-Karte, USB)  |  💿 = Festplatte")
    print("=" * 80)
    
    # Geräteauswahl
    while True:
        try:
            choice = input(f"\n➜ Wähle ein Laufwerk [1-{len(selectable_devices)}] oder 'q' zum Abbrechen: ").strip()
            
            if choice.lower() == 'q':
                print("Abgebrochen.")
                return None
            
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(selectable_devices):
                selected = selectable_devices[choice_num - 1]
                
                # Sicherheitswarnung anzeigen
                print("\n" + "⚠️ " * 20)
                print("⚠️  WARNUNG: ALLE DATEN AUF DIESEM GERÄT WERDEN GELESEN!")
                print("⚠️ " * 20)
                print(f"\nAusgewähltes Gerät: {selected['path']}")
                print(f"Größe: {selected['device'].get('size', 'N/A')}")
                
                if selected['device'].get('model'):
                    print(f"Modell: {selected['device'].get('model')}")
                
                # Prüfen ob Partitionen gemountet sind
                mounted_parts = []
                for child in selected['device'].get('children', []):
                    if child.get('mountpoint'):
                        mounted_parts.append(f"{child['name']} -> {child['mountpoint']}")
                
                if mounted_parts:
                    print("\n⚠️  ACHTUNG: Folgende Partitionen sind gemountet:")
                    for mp in mounted_parts:
                        print(f"   - {mp}")
                    print("\n💡 Tipp: Unmounten mit: sudo umount /dev/...")
                
                # Finale Bestätigung
                confirm = input(f"\n❓ Wirklich von {selected['path']} ein Backup erstellen? (JA/nein): ").strip()
                
                if confirm == 'JA':
                    return selected['path']
                else:
                    print("❌ Abgebrochen. Du musst 'JA' (Großbuchstaben) eingeben zur Bestätigung.")
                    return None
            else:
                print(f"❌ Bitte eine Zahl zwischen 1 und {len(selectable_devices)} eingeben!")
                
        except ValueError:
            print("❌ Ungültige Eingabe! Bitte eine Zahl eingeben.")
        except KeyboardInterrupt:
            print("\n\nAbgebrochen.")
            return None


class SDBackup:
    def __init__(self, source_device, output_file, block_size="4M"):
        self.source_device = source_device
        self.output_file = output_file
        self.block_size = block_size
        
    def get_device_size(self):
        """Ermittelt die Größe des Quellgeräts in Bytes"""
        try:
            result = subprocess.run(
                ['blockdev', '--getsize64', self.source_device],
                capture_output=True,
                text=True,
                check=True
            )
            return int(result.stdout.strip())
        except subprocess.CalledProcessError as e:
            print(f"❌ Fehler beim Ermitteln der Gerätegröße: {e}")
            sys.exit(1)
    
    def format_size(self, bytes_size):
        """Formatiert Bytes in lesbare Größe"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} PB"
    
    def dd_backup(self):
        """Erstellt das DD-Backup mit Statusanzeige"""
        print(f"\n🔍 Erstelle Backup von {self.source_device}")
        print(f"📁 Zieldatei: {self.output_file}")
        
        # Gerätegröße ermitteln
        device_size = self.get_device_size()
        print(f"💾 Gerätegröße: {self.format_size(device_size)}")
        
        # Prüfen ob Ausgabedatei bereits existiert
        if os.path.exists(self.output_file):
            response = input(f"⚠️  Datei {self.output_file} existiert bereits. Überschreiben? (j/n): ")
            if response.lower() != 'j':
                print("Abgebrochen.")
                sys.exit(0)
        
        print("\n📋 Starte dd-Kopiervorgang...")
        print("=" * 60)
        
        # dd Kommando mit Status-Ausgabe
        dd_cmd = [
            'dd',
            f'if={self.source_device}',
            f'of={self.output_file}',
            f'bs={self.block_size}',
            'status=progress',
            'conv=fsync'
        ]
        
        try:
            # dd mit sudo ausführen
            cmd = ['sudo'] + dd_cmd
            print(f"🔧 Befehl: {' '.join(cmd)}\n")
            
            start_time = time.time()
            
            # dd ausführen und Output direkt anzeigen
            process = subprocess.Popen(
                cmd,
                stderr=subprocess.STDOUT,
                stdout=subprocess.PIPE,
                universal_newlines=True,
                bufsize=1
            )
            
            # Ausgabe in Echtzeit anzeigen
            for line in process.stdout:
                print(line, end='')
            
            process.wait()
            
            if process.returncode != 0:
                print(f"\n❌ dd-Backup fehlgeschlagen mit Exit-Code {process.returncode}")
                sys.exit(1)
            
            elapsed_time = time.time() - start_time
            print(f"\n✅ Backup erfolgreich erstellt in {elapsed_time:.1f} Sekunden")
            print("=" * 60)
            
            # Größe der erstellten Datei anzeigen
            file_size = os.path.getsize(self.output_file)
            print(f"📊 Backup-Größe: {self.format_size(file_size)}")
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Backup durch Benutzer abgebrochen!")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Fehler beim Backup: {e}")
            sys.exit(1)
    
    def check_pishrink(self):
        """Prüft ob pishrink verfügbar ist"""
        try:
            result = subprocess.run(
                ['which', 'pishrink.sh'],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
            
            # Alternative Pfade prüfen
            common_paths = [
                '/usr/local/bin/pishrink.sh',
                '/usr/bin/pishrink.sh',
                './pishrink.sh'
            ]
            
            for path in common_paths:
                if os.path.exists(path) and os.access(path, os.X_OK):
                    return path
            
            return None
            
        except Exception:
            return None
    
    def shrink_image(self):
        """Verkleinert das Image mit pishrink"""
        print("\n\n🔄 Starte Verkleinerung mit pishrink...")
        print("=" * 60)
        
        pishrink_path = self.check_pishrink()
        
        if not pishrink_path:
            print("⚠️  pishrink.sh nicht gefunden!")
            print("\n📥 Installation:")
            print("   wget https://raw.githubusercontent.com/Drewsif/PiShrink/master/pishrink.sh")
            print("   chmod +x pishrink.sh")
            print("   sudo mv pishrink.sh /usr/local/bin/")
            
            response = input("\nTrotzdem fortfahren ohne Verkleinerung? (j/n): ")
            if response.lower() != 'j':
                sys.exit(1)
            return False
        
        print(f"✓ pishrink gefunden: {pishrink_path}")
        
        # Originalgröße ermitteln
        original_size = os.path.getsize(self.output_file)
        print(f"📊 Originalgröße: {self.format_size(original_size)}")
        
        # Erstelle Namen für verkleinerte Datei
        # Entferne .img Extension und füge _shrunk.img hinzu
        if self.output_file.endswith('.img'):
            shrunk_file = self.output_file[:-4] + '_shrunk.img'
        else:
            shrunk_file = self.output_file + '_shrunk'
        
        print(f"📁 Verkleinertes Image: {shrunk_file}")
        
        try:
            start_time = time.time()
            
            # pishrink mit zwei Dateien ausführen (vermeidet Loop-Device Probleme)
            cmd = ['sudo', pishrink_path, '-v', self.output_file, shrunk_file]
            print(f"🔧 Befehl: {' '.join(cmd)}\n")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            # Ausgabe in Echtzeit anzeigen
            for line in process.stdout:
                print(line, end='')
            
            process.wait()
            
            if process.returncode != 0:
                print(f"\n⚠️  pishrink wurde mit Exit-Code {process.returncode} beendet")
                print("💡 Tipp: Versuche das verkürzte Image manuell zu erstellen mit:")
                print(f"   sudo pishrink.sh {self.output_file} {shrunk_file}")
                return False
            
            elapsed_time = time.time() - start_time
            
            # Neue Größe ermitteln
            if os.path.exists(shrunk_file):
                new_size = os.path.getsize(shrunk_file)
                saved_space = original_size - new_size
                percentage = (saved_space / original_size) * 100
                
                print(f"\n✅ Verkleinerung erfolgreich in {elapsed_time:.1f} Sekunden")
                print("=" * 60)
                print(f"📊 Original: {self.format_size(original_size)} -> {self.output_file}")
                print(f"📊 Verkleinert: {self.format_size(new_size)} -> {shrunk_file}")
                print(f"💾 Ersparnis: {self.format_size(saved_space)} ({percentage:.1f}%)")
                
                # Frage ob Original gelöscht werden soll
                print("\n" + "-" * 60)
                response = input("❓ Original-Image löschen um Platz zu sparen? (j/n): ").strip().lower()
                if response == 'j':
                    try:
                        os.remove(self.output_file)
                        print(f"✅ {self.output_file} gelöscht")
                        print(f"📁 Verbleibendes Image: {shrunk_file}")
                    except Exception as e:
                        print(f"⚠️  Fehler beim Löschen: {e}")
                else:
                    print(f"💾 Beide Images behalten:")
                    print(f"   - Original: {self.output_file}")
                    print(f"   - Verkleinert: {shrunk_file}")
                
                return True
            else:
                print(f"\n⚠️  Verkleinertes Image {shrunk_file} wurde nicht erstellt")
                return False
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Verkleinerung durch Benutzer abgebrochen!")
            # Versuche unvollständiges shrunk file zu löschen
            if os.path.exists(shrunk_file):
                try:
                    os.remove(shrunk_file)
                    print(f"🗑️  Unvollständiges Image {shrunk_file} gelöscht")
                except:
                    pass
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Fehler bei der Verkleinerung: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description='SD-Karten Backup mit dd und pishrink',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  %(prog)s                                    # Interaktive Geräteauswahl
  %(prog)s /dev/sdb backup.img                # Direktes Backup
  %(prog)s /dev/mmcblk0 raspi-backup.img
  %(prog)s /dev/sdb backup.img --no-shrink
  %(prog)s /dev/sdb backup.img --block-size 1M

Hinweis: Das Skript benötigt sudo-Rechte für dd und pishrink.
        """
    )
    
    parser.add_argument(
        'device',
        nargs='?',
        help='Quellgerät (z.B. /dev/sdb oder /dev/mmcblk0). Wenn nicht angegeben: interaktive Auswahl'
    )
    
    parser.add_argument(
        'output',
        nargs='?',
        help='Ausgabedatei (Standard: backup_YYYYMMDD_HHMMSS.img)'
    )
    
    parser.add_argument(
        '--block-size', '-b',
        default='4M',
        help='Block-Größe für dd (Standard: 4M)'
    )
    
    parser.add_argument(
        '--no-shrink',
        action='store_true',
        help='Keine Verkleinerung mit pishrink durchführen'
    )
    
    args = parser.parse_args()
    
    # Interaktive Geräteauswahl wenn kein Device angegeben
    if args.device is None:
        args.device = select_device_interactive()
        if args.device is None:
            sys.exit(0)
    else:
        # Prüfen ob Gerät existiert
        if not os.path.exists(args.device):
            print(f"❌ Fehler: Gerät {args.device} nicht gefunden!")
            print("💡 Tipp: Starte das Skript ohne Parameter für interaktive Auswahl")
            sys.exit(1)
        
        # Prüfen ob es ein Block-Device ist
        if not os.path.isdir('/sys/block/' + os.path.basename(args.device).rstrip('0123456789')):
            print(f"⚠️  Warnung: {args.device} scheint kein Block-Device zu sein!")
            response = input("Trotzdem fortfahren? (j/n): ")
            if response.lower() != 'j':
                sys.exit(0)
    
    # Standard-Ausgabedatei wenn nicht angegeben
    if args.output is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        device_name = os.path.basename(args.device)
        args.output = f'backup_{device_name}_{timestamp}.img'
    
    print("\n" + "=" * 60)
    print("🔧 SD-Karten Backup Tool")
    print("=" * 60)
    
    # Backup-Objekt erstellen
    backup = SDBackup(args.device, args.output, args.block_size)
    
    # DD-Backup durchführen
    if backup.dd_backup():
        # Optional pishrink ausführen
        if not args.no_shrink:
            backup.shrink_image()
        else:
            print("\n⏭️  Verkleinerung übersprungen (--no-shrink)")
    
    print("\n" + "=" * 60)
    print("🎉 Fertig!")
    print("=" * 60)


if __name__ == '__main__':
    main()
