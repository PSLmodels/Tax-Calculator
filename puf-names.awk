# puf-names.awk changes header row variable names
# USAGE IN OSPC/tax-calculator DIRECTORY:
#       awk -f puf-names.awk ../tax-calculator-data/puf.csv > puf.csv

NR==1 {
    row = $0
    if ( sub(/agir1/, "AGIR1", row) != 1 ) { print ERROR; exit 1 }
    if ( sub(/dsi/, "DSI", row) != 1 ) { print ERROR; exit 1 }
    if ( sub(/efi/, "EFI", row) != 1 ) { print ERROR; exit 1 }
    if ( sub(/eic/, "EIC", row) != 1 ) { print ERROR; exit 1 }
    if ( sub(/elect/, "ELECT", row) != 1 ) { print ERROR; exit 1 }
    if ( sub(/fded/, "FDED", row) != 1 ) { print ERROR; exit 1 }
    if ( sub(/flpdyr/, "FLPDYR", row) != 1 ) { print ERROR; exit 1 }
    if ( sub(/flpdmo/, "FLPDMO", row) != 1 ) { print ERROR; exit 1 }
    if ( sub(/ie/, "IE", row) != 1 ) { print ERROR; exit 1 }
    if ( sub(/mars/, "MARS", row) != 1 ) { print ERROR; exit 1 }
    if ( sub(/midr/, "MIDR", row) != 1 ) { print ERROR; exit 1 }
    if ( sub(/prep/, "PREP", row) != 1 ) { print ERROR; exit 1 }
    if ( sub(/schb/, "SCHB", row) != 1 ) { print ERROR; exit 1 }
    if ( sub(/schcf/, "SCHCF", row) != 1 ) { print ERROR; exit 1 }
    if ( sub(/sche/, "SCHE", row) != 1 ) { print ERROR; exit 1 }
    if ( sub(/tform/, "TFORM", row) != 1 ) { print ERROR; exit 1 }
    if ( sub(/txst/, "TXST", row) != 1 ) { print ERROR; exit 1 }
    if ( sub(/xfpt/, "XFPT", row) != 1 ) { print ERROR; exit 1 }
    if ( sub(/xfst/, "XFST", row) != 1 ) { print ERROR; exit 1 }
    if ( sub(/xocah/, "XOCAH", row) != 1 ) { print ERROR; exit 1 }
    if ( sub(/xocawh/, "XOCAWH", row) != 1 ) { print ERROR; exit 1 }
    if ( sub(/xoodep/, "XOODEP", row) != 1 ) { print ERROR; exit 1 }
    if ( sub(/xopar/, "XOPAR", row) != 1 ) { print ERROR; exit 1 }
    if ( sub(/xtot/, "XTOT", row) != 1 ) { print ERROR; exit 1 }
    if ( sub(/recid/, "RECID", row) != 1 ) { print ERROR; exit 1 }
    if ( sub(/wsamp/, "WSAMP", row) != 1 ) { print ERROR; exit 1 }
    if ( sub(/txrt/, "TXRT", row) != 1 ) { print ERROR; exit 1 }
    print row
}

NR>1 {
    print $0
}
