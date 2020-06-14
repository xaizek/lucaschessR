//---Compilare con:                       ldc2 -O acquad.d
enum string VERSIONE = "3.9.1 LDC";

import std.stdio;
import std.string;
import std.random;
import std.math;
import std.algorithm;
import std.datetime;
import core.thread;
import std.conv;
import std.file;
import std.typecons;
import core.memory;

//-----------------------Variabili globali-----------------------------------------
string A_CHI_TOCCA = "bianco";
bool LOGFILE = false;
bool LOGMINMAX = false;
char[9][9] SCACCHIERA01; // L'indice 0 non lo uso cosi' e' comodo da 1 a 8
char[9][9] SCACCHIERA02; // Scacchiera provvisoria per simulare le mosse
int[string] DATABASE_VOTAZIONE; // Array associativo che contiene linea esaminata e il VERO VOTO della linea simulata
string[][] tabella_minimax; // Usato in minimax()
string[] array_stringa_linee; // Usato in minimax()
//---------------------------------------------------------------------------------

void main()
{
    int uci_exit;

    //--------------------------------Riserva spazio------------------------------------

    tabella_minimax.reserve(1_000_000);
    array_stringa_linee.reserve(1_000_000);
    //----------------------------------------------------------------------------------

    writeln("\n\n\nAcquaD is ready to Play... and to Lose...\n");
    writeln("Type 'help' for the list of commands\n\n");
    if (LOGFILE == true)
        append("acquad.log", "===========================================\r\n");
    reset_scacchiera();
    SCACCHIERA02 = SCACCHIERA01;
    while (1)
    {
        uci_exit = comandi_uci(); //--- Processa l'interfaccia UCI
        if (uci_exit == 1)
            return;
    }
}

//===============================================================================
int comandi_uci()
{
    string comando, mossa, linea;
    int TempoBianco, TempoNero, TempoDiPensamento;
    bool flag_visualizza_info_una_volta_sola;
    int inizio, fine;
    int voto;
    string best_move;
    bool flag_info;
    int secondi_trascorsi = 0;
    comando = readln();
    if (LOGFILE == true)
        append("acquad.log", "GUI: " ~ comando ~ "\r\n");
    // ------------------------------------------------
    if (indexOf(comando, "help\n") >= 0)
    {
        writeln("\nList of the commands in AcquaD Chess Engine");
        writeln("Commands with an asterisk (*) are only available in AcquaD Chess Engine\n");
        writeln("  uci");
        writeln("  ucinewgame");
        writeln("  isready");
        writeln("  quit");
        writeln("  go/stop");
        writeln("  position startpos");
        writeln("  position fen");
        writeln("* setoption name LogFile value true/false");
        writeln("* setoption name LogMinMax value true/false");
        writeln("* help");
        writeln("* show                   -----> shows the chessboards");
        writeln("* print var              -----> shows main variables");
        writeln("* print evaluation       -----> shows moves and evaluations");
        writeln("* save evaluation        -----> saves moves and evaluations to file 'evaluation.txt'");
        writeln("* cls                    -----> clears the screen");
        writeln();
        return (0);
    }
    // ------------------------------------------------
    if (comando == "\n")
    {
        return (0);
    }
    // ------------------------------------------------
    if (indexOf(comando, "uci\n") >= 0)
    {
        rispondi_alla_gui("id name AcquaD (ver. " ~ VERSIONE ~ ")");
        rispondi_alla_gui("id author Giovanni Di Maria");
        rispondi_alla_gui("option name LogFile type check default false");
        rispondi_alla_gui("option name LogMinMax type check default false");
        rispondi_alla_gui("uciok");
        writeln();
        return (0);
    }
    // ------------------------------------------------
    if (indexOf(comando, "ucinewgame\n") >= 0)
    {
        reset_scacchiera();
        A_CHI_TOCCA = "bianco";
        SCACCHIERA02 = SCACCHIERA01;
        return (0);
    }
    // ------------------------------------------------
    if (indexOf(comando, "isready\n") >= 0)
    {
        rispondi_alla_gui("readyok");
        return (0);
    }
    // ------------------------------------------------
    if (indexOf(comando, "quit\n") >= 0)
    {
        return (1);
    }
    // ------------------------------------------------
    if (indexOf(comando, "go") >= 0 || indexOf(comando, "stop") >= 0)
    {

        if (indexOf(comando, "go depth") == -1) // Compatibilita con Lucas Chess
        {

            //------Determina wtime-----
            inizio = cast(int) indexOf(comando, "wtime") + 6;
            for (int k = inizio; k < comando.length; k++)
                if (comando[k] < '0' || comando[k] > '9')
                {
                    fine = k;
                    break;
                }
            TempoBianco = 0;
            if (fine > 0)
                TempoBianco = to!int(comando[inizio .. fine]);
            //------Determina btime-----
            inizio = cast(int) indexOf(comando, "btime") + 6;
            for (int k = inizio; k < comando.length; k++)
                if (comando[k] < '0' || comando[k] > '9')
                {
                    fine = k;
                    break;
                }
            TempoNero = 0;
            if (fine > 0)
                TempoNero = to!int(comando[inizio .. fine]);
        }
        if (indexOf(comando, "go depth") >= 0) // Compatibilita con Lucas Chess
        {
            TempoBianco = 120000;
            TempoNero = 120000;
        }
        //-----------------------------------------
        SysTime t1 = Clock.currTime();
        int linee_esaminate = 0;

        //----------------------Prova a liberare memoria RAM -----------
        DATABASE_VOTAZIONE.clear;
        //--------------------------------------------------------------
        while (1)
        {
            linee_esaminate++;
            SCACCHIERA02 = SCACCHIERA01; // Fa una copia della scacchiera originale e lavora sulla copia
            linea = "";
            voto = 0;
            //----Stabilisce a chi tocca;
            if (A_CHI_TOCCA == "bianco")
            {
                TempoDiPensamento = TempoBianco / 40;
                //----------------
                mossa = simula_mossa("bianco");
                linea ~= mossa ~= " ";
                //----------------
                mossa = simula_mossa("nero");
                linea ~= mossa ~= " ";
                //----------------
                mossa = simula_mossa("bianco");
                linea ~= mossa ~= " ";
                //----------------
                mossa = simula_mossa("nero");
                voto = valutazione(SCACCHIERA02, "nero"); // Effettua la Funzione di Valutazione sulla SCACCHIERA02
                linea ~= mossa ~= " ";

                DATABASE_VOTAZIONE[linea] = voto; // Voto delle mosse simulate in Array Associativo

            }
            if (A_CHI_TOCCA == "nero")
            {
                TempoDiPensamento = TempoNero / 40;
                //----------------
                mossa = simula_mossa("nero");
                linea ~= mossa ~= " ";
                //----------------
                mossa = simula_mossa("bianco");
                linea ~= mossa ~= " ";
                //----------------
                mossa = simula_mossa("nero");
                linea ~= mossa ~= " ";
                //----------------
                mossa = simula_mossa("bianco");
                voto = valutazione(SCACCHIERA02, "bianco"); // Effettua la Funzione di Valutazione sulla SCACCHIERA02
                linea ~= mossa ~= " ";

                DATABASE_VOTAZIONE[linea] = voto; // Voto delle mosse simulate in Array Associativo

            }
            //-----Il tempo di pensamento e' scaduto?-------
            SysTime t2 = Clock.currTime();
            int diff = cast(int)(t2 - t1).total!"msecs";
            if (diff >= TempoDiPensamento)
                break;

            //----------Visualizza INFO durante scelta delle mosse OGNI tanto-------
            if( (linee_esaminate % 3000) == 0)
            {
                string stringa_info = "info depth 4 ";
                stringa_info ~= "nodes " ~ to!string(linee_esaminate);
                stringa_info ~= " pv " ~ linea;
                rispondi_alla_gui(stringa_info);
            }
        }

        //====================================MINIMAX========================
        //------------------------------minimax(DATABASE_VOTAZIONE, colore_ultimo_noto);
        if (A_CHI_TOCCA == "bianco")
            best_move = minimax(DATABASE_VOTAZIONE, "nero"); // il COLORE e' quello dell'ultimo nodo dell'albero
        if (A_CHI_TOCCA == "nero")
            best_move = minimax(DATABASE_VOTAZIONE, "bianco"); // il COLORE e' quello dell'ultimo nodo dell'albero

        //================Determina migliore mossa=============
        string stringa_info = "info depth 4 " ~ "nodes " ~ to!string(linee_esaminate);
        rispondi_alla_gui(stringa_info);
        rispondi_alla_gui("bestmove " ~ best_move);

        return (0);
    }
    // ------------------------------------------------
    if (indexOf(comando, "position startpos\n") >= 0)
    {
        reset_scacchiera();
        SCACCHIERA02 = SCACCHIERA01;
        A_CHI_TOCCA = "bianco";
        return (0);
    }
    // ------------------------------------------------
    if (indexOf(comando, "position startpos moves") >= 0)
    {
        reset_scacchiera();
        string[] Tokens = split(comando, " "); // ----Tokenizza le mosse dalla GUI
        for (int k = 0; k < Tokens.length; k++)
            Tokens[k] = strip(Tokens[k], "\n"); //---Toglie eventuale "\n" finale di ogni elemento
        Tokens = Tokens.remove(0); // Elimina "position"
        Tokens = Tokens.remove(0); // Elimina "startpos"
        Tokens = Tokens.remove(0); // Elimina "moves"
        // -------Stabilisce di chi e' il TRATTO-----
        if (Tokens.length % 2 == 1)
            A_CHI_TOCCA = "nero";
        else
            A_CHI_TOCCA = "bianco";

        foreach (m; Tokens)
        {
            aggiorna_scacchiera_da_mossa(m, SCACCHIERA01);
        }
        SCACCHIERA02 = SCACCHIERA01;
        return (0);
    }
    // ------------------------------------------------
    if (indexOf(comando, "position fen") >= 0)
    {
        scacchiera_da_fen(comando);
        SCACCHIERA02 = SCACCHIERA01;
        return (0);
    }
    // ------------------------------------------------
    if (indexOf(comando, "setoption name LogFile value true\n") >= 0)
    {
        LOGFILE = true;
        return (0);
    }
    // ------------------------------------------------
    if (indexOf(comando, "setoption name LogFile value false\n") >= 0)
    {
        LOGFILE = false;
        return (0);
    }
    // ------------------------------------------------
    if (indexOf(comando, "setoption name LogMinMax value true\n") >= 0)
    {
        LOGMINMAX = true;
        return (0);
    }
    // ------------------------------------------------
    if (indexOf(comando, "setoption name LogMinMax value false\n") >= 0)
    {
        LOGMINMAX = false;
        return (0);
    }
    // ------------------------------------------------
    if (indexOf(comando, "show\n") >= 0)
    {
        show();
        return (0);
    }
    // ------------------------------------------------
    if (indexOf(comando, "print var\n") >= 0)
    {
        printvar();
        return (0);
    }
    // ------------------------------------------------
    if (indexOf(comando, "print evaluation\n") >= 0)
    {
        foreach (k, v; DATABASE_VOTAZIONE)
        {
            writefln("%s  %10.4f", k, v);
        }
        return (0);
    }
    // ------------------------------------------------
    if (indexOf(comando, "save evaluation\n") >= 0)
    {
        File file = File("evaluation.txt", "w");
        foreach (k, v; DATABASE_VOTAZIONE)
        {
            writefln("%s  %10.4f", k, v);
            file.writefln("%s  %10.4f", k, v);
        }
        file.close();
        writeln("\n\nData are stored to file 'evaluation.txt'");
        return (0);
    }
    // ------------------------------------------------
    if (indexOf(comando, "cls\n") >= 0)
    {
        cls();
        return (0);
    }
    // ------------------------------------------------
    writeln("Command not recognized");
    return (0);
}

//===============================================================================
void rispondi_alla_gui(string messaggio)
{
    stdout.writeln(messaggio);
    stdout.flush();
    if (LOGFILE == true)
        append("acquad.log", "Engine: " ~ messaggio ~ "\r\n");
}

//===============================================================================
void reset_scacchiera()
{
    int x, y;
    // -------Svuota scacchiera---------
    for (x = 1; x <= 8; x++)
        for (y = 1; y <= 8; y++)
            SCACCHIERA01[x][y] = '-';
    // ----Pedoni-------
    for (x = 1; x <= 8; x++)
    {
        SCACCHIERA01[x][2] = 'P';
        SCACCHIERA01[x][7] = 'p';
    }
    // ------Cavalli------
    SCACCHIERA01[2][1] = 'N';
    SCACCHIERA01[7][1] = 'N';
    SCACCHIERA01[2][8] = 'n';
    SCACCHIERA01[7][8] = 'n';
    // ------Alfieri--------
    SCACCHIERA01[3][1] = 'B';
    SCACCHIERA01[6][1] = 'B';
    SCACCHIERA01[3][8] = 'b';
    SCACCHIERA01[6][8] = 'b';
    // ----Torri---------
    SCACCHIERA01[1][1] = 'R';
    SCACCHIERA01[8][1] = 'R';
    SCACCHIERA01[1][8] = 'r';
    SCACCHIERA01[8][8] = 'r';
    // -----Donne-----
    SCACCHIERA01[4][1] = 'Q';
    SCACCHIERA01[4][8] = 'q';
    // -----Re-------
    SCACCHIERA01[5][1] = 'K';
    SCACCHIERA01[5][8] = 'k';
    return;
}

//===============================================================================
void show()
{
    int x, y;
    writeln();
    writeln("           SCACCHIERA01                     SCACCHIERA02"); // Bordi superiori
    writeln();
    writeln("     ------------------------         ------------------------"); // Bordi superiori
    for (y = 8; y >= 1; y--)
    {
        //--------------------Mostra SCACCHIERA01----------------
        write("   ", y, " |"); // Bordo sinistro
        for (x = 1; x <= 8; x++)
        {
            write(SCACCHIERA01[x][y]);
            if (x < 8)
                write("  ");
        }
        write("|"); // Bordo destro
        //--------------------Mostra SCACCHIERA02----------------
        write("       ", y, " |"); // Bordo sinistro
        for (x = 1; x <= 8; x++)
        {
            write(SCACCHIERA02[x][y]);
            if (x < 8)
                write("  ");
        }
        write("|"); // Bordo destro

        writeln();
    }
    writeln("     ------------------------         ------------------------"); // Bordo inferiore
    writeln("      a  b  c  d  e  f  g  h           a  b  c  d  e  f  g  h");
    writeln();
    return;
}

//===============================================================================
void printvar()
{
    int x, y;
    writeln();
    writeln("List of main variables in AcquaD Chess Engine");
    writeln("--------------------------------------------");
    writeln("A_CHI_TOCCA:    ", A_CHI_TOCCA);
    writeln("LOGFILE:        ", LOGFILE);
    writeln("LOGMINMAX:      ", LOGMINMAX);
    writeln();
    return;
}

//===============================================================================
void cls()
{
    for (int k = 1; k <= 100; ++k)
        writeln();
    return;
}

//===============================================================================
void scacchiera_da_fen(string comando)
{
    // ESEMPIO: rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
    int k, x, y;
    int nPosizioneSpazio;
    string stringa_fen_originale = comando[indexOf(comando, "fen") + 4 .. comando.length];
    string stringa_scacchiera_64 = "";

    //--- Costruisce stringa lineare dei pezzi da FEN: esempio 1rRqQ3 = " rRqQ   "
    foreach (ch; stringa_fen_originale)
    {
        if (ch == ' ') // Se vede uno spazio ESCE
            break;
        if (ch >= 'A' && ch <= 'Z')
            stringa_scacchiera_64 ~= ch; // Aggiunge pezzi bianchi
        if (ch >= 'a' && ch <= 'z')
            stringa_scacchiera_64 ~= ch; // Aggiunge pezzi neri
        if (ch >= '1' && ch <= '8')
            for (k = 49; k <= ch; k++)
                stringa_scacchiera_64 ~= '-'; // Aggiunge case vuote
    }
    // ------Dispone i pezzi sulla scacchiera secondo la stringa LINEARE------
    k = 0;
    for (y = 8; y >= 1; y--)
        for (x = 1; x <= 8; x++)
        {
            SCACCHIERA01[x][y] = stringa_scacchiera_64[k];
            k++;
        }

    // ------Cerca lo spazio per determinare A CHI TOCCA------
    nPosizioneSpazio = indexOf(stringa_fen_originale, " ");
    // -------Stabilisce di chi e' il TRATTO --- ("w" = al Bianco, "b" = al Nero)---
    if (stringa_fen_originale[nPosizioneSpazio + 1] == 'b')
        A_CHI_TOCCA = "nero";
    if (stringa_fen_originale[nPosizioneSpazio + 1] == 'w')
        A_CHI_TOCCA = "bianco";
}

//===============================================================================
void aggiorna_scacchiera_da_mossa(string mossa, ref char[9][9] scacchiera_di_comodo)
{
    int nPartenza_x = cast(int) mossa[0] - 96;
    int nPartenza_y = cast(int) mossa[1] - 48;
    int nArrivo_x = cast(int) mossa[2] - 96;
    int nArrivo_y = cast(int) mossa[3] - 48;

    // ----------Arrocco corto bianco-------------
    if (mossa == "e1g1" && scacchiera_di_comodo[5][1] == 'K')
    {
        scacchiera_di_comodo[5][1] = '-';
        scacchiera_di_comodo[8][1] = '-';
        scacchiera_di_comodo[7][1] = 'K';
        scacchiera_di_comodo[6][1] = 'R';
    }

    // ----------Arrocco lungo bianco-------------
    else if (mossa == "e1c1" && scacchiera_di_comodo[5][1] == 'K')
    {
        scacchiera_di_comodo[5][1] = '-';
        scacchiera_di_comodo[1][1] = '-';
        scacchiera_di_comodo[3][1] = 'K';
        scacchiera_di_comodo[4][1] = 'R';
    }
    // ----------Arrocco corto nero-------------
    else if (mossa == "e8g8" && scacchiera_di_comodo[5][8] == 'k')
    {
        scacchiera_di_comodo[5][8] = '-';
        scacchiera_di_comodo[8][8] = '-';
        scacchiera_di_comodo[7][8] = 'k';
        scacchiera_di_comodo[6][8] = 'r';
    }

    // ----------Arrocco lungo nero-------------
    else if (mossa == "e8c8" && scacchiera_di_comodo[5][8] == 'k')
    {
        scacchiera_di_comodo[5][8] = '-';
        scacchiera_di_comodo[1][8] = '-';
        scacchiera_di_comodo[3][8] = 'k';
        scacchiera_di_comodo[4][8] = 'r';
    }
    // ----------Pedone cattura EnPassant-------------
    else if ((scacchiera_di_comodo[nPartenza_x][nPartenza_y] == 'p' || scacchiera_di_comodo[nPartenza_x][nPartenza_y] == 'P') && scacchiera_di_comodo[nArrivo_x][nArrivo_y] == '-' && abs(nPartenza_x - nArrivo_x) == 1 && abs(nPartenza_y - nArrivo_y) == 1)
    {
        scacchiera_di_comodo[nArrivo_x][nArrivo_y] = scacchiera_di_comodo[nPartenza_x][nPartenza_y];
        scacchiera_di_comodo[nPartenza_x][nPartenza_y] = '-';
        scacchiera_di_comodo[nArrivo_x][nPartenza_y] = '-';
    }
    // ----------Sposta pezzo-------------
    else
    {
        scacchiera_di_comodo[nArrivo_x][nArrivo_y] = scacchiera_di_comodo[nPartenza_x][nPartenza_y];
        scacchiera_di_comodo[nPartenza_x][nPartenza_y] = '-';
    }

    // ----------Promozione-------------
    if (mossa.length == 5 && nArrivo_y > nPartenza_y) // Sta promuovendo il Bianco: a7a8
        scacchiera_di_comodo[nArrivo_x][nArrivo_y] = cast(char)(mossa[4] - 32); // Pezzo MAIUSCOLO: es: a7a8Q
    if (mossa.length == 5 && nArrivo_y < nPartenza_y) // Sta promuovendo il Nero: c2c1
        scacchiera_di_comodo[nArrivo_x][nArrivo_y] = cast(char)(mossa[4]); // Pezzo minuscolo: es: a2a1q

}

//===============================================================================
//---------------------------------------------ATTENZIONE. QUI SI LAVORA SULLA SCACCHIERA02
string simula_mossa(string colore)
{
    ubyte casa_iniziale_x, casa_iniziale_y;
    ubyte casa_finale_x, casa_finale_y;
    byte differenza_x, differenza_y;
    byte stepx, stepy;
    bool pezzo_ostacolato;
    byte xx, yy;
    string stringa_finale;
    string tutti_i_pezzi_col_tratto, tutti_i_pezzi_opponenti;
    char re_col_tratto;
    int numero_tentativi = 0;
    //auto rng = Random(unpredictableSeed);
    //auto rng = Xorshift(unpredictableSeed);

    //---------Inizializza variabili per il Bianco o per il Nero-------
    if (colore == "bianco")
    {
        tutti_i_pezzi_col_tratto = "KQRBNP"; // Pezzi che hanno il diritto di muovere
        tutti_i_pezzi_opponenti = "kqrbnp"; // Pezzi della controparte
        re_col_tratto = 'K'; // Il re che muove
    }
    if (colore == "nero")
    {
        tutti_i_pezzi_col_tratto = "kqrbnp"; // Pezzi che hanno il diritto di muovere
        tutti_i_pezzi_opponenti = "KQRBNP"; // Pezzi della controparte
        re_col_tratto = 'k'; // Il re che muove
    }
    //----------------------INIZIA L'ESTRAZIONE DELLA MOSSA----------------

    while (1)
    {

        //--------------------Sceglie a caso una casa di partenza------------------

        while (1)
        {
            casa_iniziale_x = cast(ubyte)uniform(1, 9); // da 1 a 8
            casa_iniziale_y = cast(ubyte)uniform(1, 9); // da 1 a 8

            // casa_iniziale_x = uniform!ubyte(rng) % 8 + 1;
            // casa_iniziale_y = uniform!ubyte(rng) % 8 + 1;

            if (indexOf(tutti_i_pezzi_col_tratto, SCACCHIERA02[casa_iniziale_x][casa_iniziale_y]) >= 0) //--Cerca il pezzo da muovere
            {
                break;
            }
            //------Se i tentativi di ricerca sono molti, vuol dire che non trova una mossa legale, quindi e' MATTO o STALLO
            numero_tentativi++;
            string mossa="";
            if (numero_tentativi == 50000)
            {
                if(pezzo_sotto_scacco(SCACCHIERA02, re_col_tratto)==0)
                    mossa="STAL";
                else
                    mossa="MATT";
                return mossa;
            }
        }
        //--------------------Sceglie a caso una casa di arrivo------------------
        while (1)
        {
            casa_finale_x = cast(ubyte)uniform(1, 9); // da 1 a 8
            casa_finale_y = cast(ubyte)uniform(1, 9); // da 1 a 8

            // casa_finale_x = uniform!ubyte(rng) % 8 + 1;
            // casa_finale_y = uniform!ubyte(rng) % 8 + 1;

            // Se casa finale e' vuota OPPURE Se la casa finale ha pezzo della controparte (cattura)
            if (SCACCHIERA02[casa_finale_x][casa_finale_y] == '-' || indexOf(tutti_i_pezzi_opponenti, SCACCHIERA02[casa_finale_x][casa_finale_y]) >= 0)
            {
                break;
            }

        }

        //-------------------------------------------------------------------------
        //---Se il pezzo che muove e' il RE, verifica che si muove di un passo alla volta (anche se ci sono pezzi per ora non importa)-----
        if (SCACCHIERA02[casa_iniziale_x][casa_iniziale_y] == 'K' || SCACCHIERA02[casa_iniziale_x][casa_iniziale_y] == 'k')

        {
            differenza_x = cast(byte) abs(casa_iniziale_x - casa_finale_x);
            differenza_y = cast(byte) abs(casa_iniziale_y - casa_finale_y);
            if (!(differenza_x < 2 && differenza_y < 2)) //---Differenza case partenza/arrivo X o Y NON DEVE ESSERE >1
                continue; //---Ritenta estrazione
        }
        //-------------------------------------------------------------------------
        //---Se il pezzo che muove e' la TORRE, verifica che si muove in VERTICALE o ORIZZONTALE (anche se ci sono pezzi per ora non importa)-----
        if (SCACCHIERA02[casa_iniziale_x][casa_iniziale_y] == 'R' || SCACCHIERA02[casa_iniziale_x][casa_iniziale_y] == 'r')
        {
            differenza_x = cast(byte) abs(casa_iniziale_x - casa_finale_x);
            differenza_y = cast(byte) abs(casa_iniziale_y - casa_finale_y);
            if (!(differenza_x == 0 || differenza_y == 0)) //---Differenza case di partenza/arrivo X o Y DEVE ESSERE = 0
                continue; //---Ritenta estrazione
        }
        //-------------------------------------------------------------------------
        //---Se il pezzo che muove e' l'ALFIERE, verifica che si muove in DIAGONALE (anche se ci sono pezzi non importa)-----
        if (SCACCHIERA02[casa_iniziale_x][casa_iniziale_y] == 'B' || SCACCHIERA02[casa_iniziale_x][casa_iniziale_y] == 'b')
        {
            differenza_x = cast(byte) abs(casa_iniziale_x - casa_finale_x);
            differenza_y = cast(byte) abs(casa_iniziale_y - casa_finale_y);
            if (!(differenza_x == differenza_y)) //---Differenza case di partenza/arrivo X e Y DEVE ESSERE UGUALE
                continue; //---Ritenta estrazione
        }
        //-------------------------------------------------------------------------
        //---Se il pezzo che muove e' la DONNA fa le stesse cose di TORRE e ALFIERE (anche se ci sono pezzi non importa)-----
        if (SCACCHIERA02[casa_iniziale_x][casa_iniziale_y] == 'Q' || SCACCHIERA02[casa_iniziale_x][casa_iniziale_y] == 'q')
        {
            differenza_x = cast(byte) abs(casa_iniziale_x - casa_finale_x);
            differenza_y = cast(byte) abs(casa_iniziale_y - casa_finale_y);
            if (!(differenza_x == 0 || differenza_y == 0 || differenza_x == differenza_y))
                continue; //---Ritenta estrazione
        }
        //-------------------------------------------------------------------------
        //---Se il pezzo che muove e' il CAVALLO, verifica che si muove A ELLE (anche se ci sono pezzi non importa)-----
        if (SCACCHIERA02[casa_iniziale_x][casa_iniziale_y] == 'N' || SCACCHIERA02[casa_iniziale_x][casa_iniziale_y] == 'n')
        {
            differenza_x = cast(byte) abs(casa_iniziale_x - casa_finale_x);
            differenza_y = cast(byte) abs(casa_iniziale_y - casa_finale_y);
            bool c1 = (differenza_x == 1 && differenza_y == 2); //---Diff. case di partenza/arrivo X e Y DEVE ESSERE 1 e 2
            bool c2 = (differenza_x == 2 && differenza_y == 1); //---Diff. case di partenza/arrivo X e Y DEVE ESSERE 1 e 2
            if (!(c1 || c2))
                continue; //---Ritenta estrazione
        }
        //-------------------------------------------------------------------------
        //---Se il pezzo che muove e' il PEDONE BIANCO, verifica che vada AVANTI DI UNO, DUE o CATTURA-----

        if (SCACCHIERA02[casa_iniziale_x][casa_iniziale_y] == 'P')
        {
            differenza_x = cast(byte)(casa_iniziale_x - casa_finale_x);
            differenza_y = cast(byte)(casa_iniziale_y - casa_finale_y);
            bool c1 = (differenza_x == 0 && differenza_y == -2 && casa_iniziale_y == 2 && SCACCHIERA02[casa_finale_x][casa_finale_y] == '-' && SCACCHIERA02[casa_iniziale_x][casa_iniziale_y + 1] == '-'); // Spinta di 2 passi
            bool c2 = (differenza_x == 0 && differenza_y == -1 && SCACCHIERA02[casa_finale_x][casa_finale_y] == '-'); // Spinta di 1 passo
            bool c3 = (differenza_x == +1 && differenza_y == -1 && indexOf("kqrbnp", SCACCHIERA02[casa_finale_x][casa_finale_y]) >= 0); // Cattura a SX
            bool c4 = (differenza_x == -1 && differenza_y == -1 && indexOf("kqrbnp", SCACCHIERA02[casa_finale_x][casa_finale_y]) >= 0); // Cattura a DX
            if (!(c1 || c2 || c3 || c4))
                continue; //---Ritenta estrazione
        }

        //-------------------------------------------------------------------------
        //---Se il pezzo che muove e' il PEDONE NERO, verifica che vada AVANTI DI UNO, DUE o CATTURA-----
        if (SCACCHIERA02[casa_iniziale_x][casa_iniziale_y] == 'p')
        {
            differenza_x = cast(byte)(casa_iniziale_x - casa_finale_x);
            differenza_y = cast(byte)(casa_iniziale_y - casa_finale_y);
            bool c1 = (differenza_x == 0 && differenza_y == 2 && casa_iniziale_y == 7 && SCACCHIERA02[casa_finale_x][casa_finale_y] == '-' && SCACCHIERA02[casa_iniziale_x][casa_iniziale_y - 1] == '-'); // Spinta di 2 passi
            bool c2 = (differenza_x == 0 && differenza_y == 1 && SCACCHIERA02[casa_finale_x][casa_finale_y] == '-'); // Spinta di 1 passo
            bool c3 = (differenza_x == +1 && differenza_y == 1 && indexOf("KQRBNP", SCACCHIERA02[casa_finale_x][casa_finale_y]) >= 0); // Cattura a SX
            bool c4 = (differenza_x == -1 && differenza_y == 1 && indexOf("KQRBNP", SCACCHIERA02[casa_finale_x][casa_finale_y]) >= 0); // Cattura a DX
            if (!(c1 || c2 || c3 || c4))
                continue; //---Ritenta estrazione
        }
        //-------------------------------------------------------------------------
        //-------Controlla se nel proprio cammino ci sono PEZZI DEL PROPRIO COLORE o COLORE AVVERSARIO------------

        if (indexOf("KQRBkqrb", SCACCHIERA02[casa_iniziale_x][casa_iniziale_y]) >= 0)
        {
            //-----Calcola STEP X
            if (casa_finale_x > casa_iniziale_x)
                stepx = 1; //Stepx Positivo: va a DX.
            if (casa_finale_x < casa_iniziale_x)
                stepx = -1; //Stepx Negativo: va a SX.
            if (casa_finale_x == casa_iniziale_x)
                stepx = 0; //Stepx 0: resta su colonna
            //-----Calcola STEP Y
            if (casa_finale_y > casa_iniziale_y)
                stepy = 1; //Stepy Positivo: va SU.
            if (casa_finale_y < casa_iniziale_y)
                stepy = -1; //Stepy Negativo: va GIU.
            if (casa_finale_y == casa_iniziale_y)
                stepy = 0; //Stepy 0: resta su riga
            //----Inizia cammino per vedere se ci sono propri ostacoli-------
            xx = casa_iniziale_x;
            yy = casa_iniziale_y;
            pezzo_ostacolato = 0;
            while (1)
            {
                xx = cast(byte)(xx + stepx);
                yy = cast(byte)(yy + stepy);
                //----Il cammino di controllo e' arrivato nella casa di destinazione?-----
                if (xx == casa_finale_x && yy == casa_finale_y)
                    break;
                //-----Sulla strada della mossa ci sono PEZZI OSTACOLANTI-----
                if (indexOf("KQRBNPkqrbnp", SCACCHIERA02[xx][yy]) >= 0 && !(xx == casa_finale_x && yy == casa_finale_y))
                {
                    pezzo_ostacolato = 1;
                    break;
                }
            }
            if (pezzo_ostacolato == 1)
                continue; //---Ritenta estrazione
        }

        //===================Controlla se il proprio RE e' in scacco================
        //----Simula la mossa su una scacchiera provvisoria
        char[9][9] SCACCHIERA_PROVVISORIA;
        SCACCHIERA_PROVVISORIA = SCACCHIERA02;
        SCACCHIERA_PROVVISORIA[casa_finale_x][casa_finale_y] = SCACCHIERA02[casa_iniziale_x][casa_iniziale_y];
        SCACCHIERA_PROVVISORIA[casa_iniziale_x][casa_iniziale_y] = '-';
        if (pezzo_sotto_scacco(SCACCHIERA_PROVVISORIA, re_col_tratto))
            continue; //---Ritenta estrazione

        //=======================================================================
        break; //----- Se l'esecuzione del programma arriva QUI vuol dire che la MOSSA E' LEGALE e si puo' uscire dal ciclo
    }

    stringa_finale = format("%c%c%c%c", cast(char)(casa_iniziale_x + 96), cast(char)(casa_iniziale_y + 48), cast(char)(casa_finale_x + 96), cast(char)(casa_finale_y + 48));

    aggiorna_scacchiera_da_mossa(stringa_finale, SCACCHIERA02);

    return stringa_finale; // esempio d2d4
}

//===============================================================================
bool pezzo_sotto_scacco(char[9][9] SCACCHIERA, char pezzo_da_controllare)
{
    int k;
    int x, y;
    int casa_pezzo_x, casa_pezzo_y;
    bool pezzo_sotto_scacco;
    char re_minacciante, donna_minacciante, torre_minacciante, alfiere_minacciante, cavallo_minacciante, pedone_minacciante;
    string pezzi_amici;
    int[9][9] matrice_case_controllate;
    if (pezzo_da_controllare <= 90) // Se il pezzo da controllare e' BIANCO (lettera MAIUSCOLA)
    {
        re_minacciante = 'k';
        donna_minacciante = 'q';
        torre_minacciante = 'r';
        alfiere_minacciante = 'b';
        cavallo_minacciante = 'n';
        pedone_minacciante = 'p';
        pezzi_amici = "KQRBNP";
    }
    if (pezzo_da_controllare >= 97) // Se il pezzo da controllare e' NERO (lettera minuscola)
    {
        re_minacciante = 'K';
        donna_minacciante = 'Q';
        torre_minacciante = 'R';
        alfiere_minacciante = 'B';
        cavallo_minacciante = 'N';
        pedone_minacciante = 'P';
        pezzi_amici = "kqrbnp";
    }

    //================Costruisce matrice delle case controllate===========

    for (y = 8; y >= 1; y--)
        for (x = 1; x <= 8; x++)
            matrice_case_controllate[x][y] = 0;

    for (y = 8; y >= 1; y--)
        for (x = 1; x <= 8; x++)
        {
            // -----SEGNA le case CONTROLLATE: Donna o Alfiere verso in alto a destra-----
            if (SCACCHIERA[x][y] == donna_minacciante || SCACCHIERA[x][y] == alfiere_minacciante)
                for (k = 1; k <= 7; k++)
                {
                    if (x + k > 8 || y + k > 8)
                        break;
                    matrice_case_controllate[x + k][y + k] = 1;
                    if (SCACCHIERA[x + k][y + k] != '-')
                        break;
                }
            // -----SEGNA le case CONTROLLATE: Donna o Alfiere verso in basso a destra-----
            if (SCACCHIERA[x][y] == donna_minacciante || SCACCHIERA[x][y] == alfiere_minacciante)
                for (k = 1; k <= 7; k++)
                {
                    if (x + k > 8 || y - k < 1)
                        break;
                    matrice_case_controllate[x + k][y - k] = 1;
                    if (SCACCHIERA[x + k][y - k] != '-')
                        break;
                }
            // -----SEGNA le case CONTROLLATE: Donna o Alfiere verso in alto a sinistra-----
            if (SCACCHIERA[x][y] == donna_minacciante || SCACCHIERA[x][y] == alfiere_minacciante)
                for (k = 1; k <= 7; k++)
                {
                    if (x - k < 1 || y + k > 8)
                        break;
                    matrice_case_controllate[x - k][y + k] = 1;
                    if (SCACCHIERA[x - k][y + k] != '-')
                        break;
                }
            // -----SEGNA le case CONTROLLATE: Donna o Alfiere verso in basso a sinistra-----
            if (SCACCHIERA[x][y] == donna_minacciante || SCACCHIERA[x][y] == alfiere_minacciante)
                for (k = 1; k <= 7; k++)
                {
                    if (x - k < 1 || y - k < 1)
                        break;
                    matrice_case_controllate[x - k][y - k] = 1;
                    if (SCACCHIERA[x - k][y - k] != '-')
                        break;
                }
            // -----SEGNA le case CONTROLLATE: Donna o Torre verso destra-----
            if (SCACCHIERA[x][y] == donna_minacciante || SCACCHIERA[x][y] == torre_minacciante)
                for (k = 1; k <= 7; k++)
                {
                    if (x + k > 8)
                        break;
                    matrice_case_controllate[x + k][y] = 1;
                    if (SCACCHIERA[x + k][y] != '-')
                        break;
                }
            // -----SEGNA le case CONTROLLATE: Donna o Torre verso sinistra-----
            if (SCACCHIERA[x][y] == donna_minacciante || SCACCHIERA[x][y] == torre_minacciante)
                for (k = 1; k <= 7; k++)
                {
                    if (x - k < 1)
                        break;
                    matrice_case_controllate[x - k][y] = 1;
                    if (SCACCHIERA[x - k][y] != '-')
                        break;
                }
            // -----SEGNA le case CONTROLLATE: Donna o Torre verso in alto-----
            if (SCACCHIERA[x][y] == donna_minacciante || SCACCHIERA[x][y] == torre_minacciante)
                for (k = 1; k <= 7; k++)
                {
                    if (y + k > 8)
                        break;
                    matrice_case_controllate[x][y + k] = 1;
                    if (SCACCHIERA[x][y + k] != '-')
                        break;
                }
            // -----SEGNA le case CONTROLLATE: Donna o Torre verso in basso-----
            if (SCACCHIERA[x][y] == donna_minacciante || SCACCHIERA[x][y] == torre_minacciante)
                for (k = 1; k <= 7; k++)
                {
                    if (y - k < 1)
                        break;
                    matrice_case_controllate[x][y - k] = 1;
                    if (SCACCHIERA[x][y - k] != '-')
                        break;
                }
            // -----SEGNA le case CONTROLLATE: Cavallo-----
            if (SCACCHIERA[x][y] == cavallo_minacciante)
            {
                if (x + 1 <= 8 && y + 2 <= 8)
                    matrice_case_controllate[x + 1][y + 2] = 1;
                if (x + 2 <= 8 && y + 1 <= 8)
                    matrice_case_controllate[x + 2][y + 1] = 1;
                if (x + 2 <= 8 && y - 1 >= 1)
                    matrice_case_controllate[x + 2][y - 1] = 1;
                if (x + 1 <= 8 && y - 2 >= 1)
                    matrice_case_controllate[x + 1][y - 2] = 1;
                if (x - 1 >= 1 && y - 2 >= 1)
                    matrice_case_controllate[x - 1][y - 2] = 1;
                if (x - 2 >= 1 && y - 1 >= 1)
                    matrice_case_controllate[x - 2][y - 1] = 1;
                if (x - 2 >= 1 && y + 1 <= 8)
                    matrice_case_controllate[x - 2][y + 1] = 1;
                if (x - 1 >= 1 && y + 2 <= 8)
                    matrice_case_controllate[x - 1][y + 2] = 1;
            }
            // -----SEGNA le case CONTROLLATE: Re-----
            if (SCACCHIERA[x][y] == re_minacciante)
            {
                if (x + 1 <= 8 && y + 1 <= 8)
                    matrice_case_controllate[x + 1][y + 1] = 1;
                if (x + 1 <= 8)
                    matrice_case_controllate[x + 1][y] = 1;
                if (x + 1 <= 8 && y - 1 >= 1)
                    matrice_case_controllate[x + 1][y - 1] = 1;
                if (y - 1 >= 1)
                    matrice_case_controllate[x][y - 1] = 1;
                if (x - 1 >= 1 && y - 1 >= 1)
                    matrice_case_controllate[x - 1][y - 1] = 1;
                if (x - 1 >= 1)
                    matrice_case_controllate[x - 1][y] = 1;
                if (x - 1 >= 1 && y + 1 <= 8)
                    matrice_case_controllate[x - 1][y + 1] = 1;
                if (y + 1 <= 8)
                    matrice_case_controllate[x][y + 1] = 1;

            }

            // -----SEGNA le case CONTROLLATE: Pedone-----
            if (SCACCHIERA[x][y] == pedone_minacciante)
            {
                if (pedone_minacciante == 'p')
                {
                    if (x - 1 >= 1 && y - 1 >= 1)
                        matrice_case_controllate[x - 1][y - 1] = 1;
                    if (x + 1 <= 8 && y - 1 >= 1)
                        matrice_case_controllate[x + 1][y - 1] = 1;
                }
                if (pedone_minacciante == 'P')
                {
                    if (x - 1 >= 1 && y + 1 <= 8)
                        matrice_case_controllate[x - 1][y + 1] = 1;
                    if (x + 1 <= 8 && y + 1 <= 8)
                        matrice_case_controllate[x + 1][y + 1] = 1;
                }
            }
        }

    //---Cerca il pezzo da controllare nella scacchiera provvisoria-------
    for (y = 8; y >= 1; y--)
        for (x = 1; x <= 8; x++)
            if (SCACCHIERA[x][y] == pezzo_da_controllare)
            {
                casa_pezzo_x = x;
                casa_pezzo_y = y;
            }
    pezzo_sotto_scacco = 0; // Al momento il pezzo da controllare NON e' sotto scacco
    if (matrice_case_controllate[casa_pezzo_x][casa_pezzo_y] == 1)
        pezzo_sotto_scacco = 1; // Il pezzo da controllare e' in una casa controllata dall'avversario

    return pezzo_sotto_scacco;
}

//==========================Valutazione in CENTESIMI di PEDONE======================
int valutazione(char[9][9] board, string chi_ha_eseguito_ultima_mossa)
{
    //------------------Valuta quantita' di pezzi sulla scacchiera: K=30, Q=1000, R=500, B=310, N=290, P=100
    byte x, y;
    int v;
    v = 0;

    for (y = 8; y >= 1; y--)
    {
        for (x = 1; x <= 8; x++)
        {
            if (board[x][y] == 'K')
                v += 100000;
            if (board[x][y] == 'Q')
                v += 1000;
            if (board[x][y] == 'R')
                v += 500;
            if (board[x][y] == 'B')
                v += 310;
            if (board[x][y] == 'N')
                v += 290;
            if (board[x][y] == 'P')
                v += 100;
            //------------------------
            if (board[x][y] == 'k')
                v -= 100000;
            if (board[x][y] == 'q')
                v -= 1000;
            if (board[x][y] == 'r')
                v -= 500;
            if (board[x][y] == 'b')
                v -= 310;
            if (board[x][y] == 'n')
                v -= 290;
            if (board[x][y] == 'p')
                v -= 100;
        }
    }

    //------------------I pedoni che avanzano valgono di piu'
    for (x = 1; x <= 8; x++)
    {
        if (board[x][3] == 'P')
            v += 1;
        if (board[x][4] == 'P')
            v += 2;
        if (board[x][5] == 'P')
            v += 3;
        if (board[x][6] == 'P')
            v += 4;
        if (board[x][7] == 'P')
            v += 5;
        if (board[x][8] == 'P')
            v += 500;
        //------------------------
        if (board[x][6] == 'p')
            v -= 1;
        if (board[x][5] == 'p')
            v -= 2;
        if (board[x][4] == 'p')
            v -= 3;
        if (board[x][3] == 'p')
            v -= 4;
        if (board[x][2] == 'p')
            v -= 5;
        if (board[x][1] == 'p')
            v -= 500;
    }

    //------------------Penalizza doppi, tripli ecc PEDONI
    for (x = 1; x <= 8; x++)
    {
        string stringa_di_comodo = "";
        for (y = 1; y <= 8; y++)
        {
            stringa_di_comodo ~= board[x][y];
        }
        if (count(stringa_di_comodo, "P") == 2) // Es: "R-b-P-P"
            v -= 2;
        if (count(stringa_di_comodo, "P") == 3) // Es: "RPb-P-P"
            v -= 3;
        if (count(stringa_di_comodo, "p") == 2) // Es: "R-b-p-p"
            v += 2;
        if (count(stringa_di_comodo, "p") == 3) // Es: "Rpb-p-p"
            v += 3;
    }

    //--------------Malus a Cavalli su BORDO (vale anche per permettere apertura e sviluppo)------
    for (x = 1; x <= 8; x++) // Nell'ultima traversa e nella prima traversa
    {
        if (board[x][8] == 'N')
            v -= 5;
        if (board[x][1] == 'N')
            v -= 5;
        //------------------------
        if (board[x][8] == 'n')
            v += 5;
        if (board[x][1] == 'n')
            v += 5;
    }
    for (y = 1; y <= 8; y++) // Nella prima colonna e nell'ultima colonna
    {
        if (board[1][y] == 'N')
            v -= 5;
        if (board[8][y] == 'N')
            v -= 5;
        //------------------------
        if (board[1][y] == 'n')
            v += 5;
        if (board[8][y] == 'n')
            v += 5;
    }

    //--------------Malus a Alfieri su BORDO (vale anche per permettere apertura e sviluppo)------
    for (x = 1; x <= 8; x++) // Nell'ultima traversa e nella prima traversa
    {
        if (board[x][8] == 'B')
            v -= 5;
        if (board[x][1] == 'B')
            v -= 5;
        //------------------------
        if (board[x][8] == 'b')
            v += 5;
        if (board[x][1] == 'b')
            v += 5;
    }
    for (y = 1; y <= 8; y++) // Nella prima colonna e nell'ultima colonna
    {
        if (board[1][y] == 'B')
            v -= 5;
        if (board[8][y] == 'B')
            v -= 5;
        //------------------------
        if (board[1][y] == 'b')
            v += 5;
        if (board[8][y] == 'b')
            v += 5;
    }

    //------------------Bonus COLONNE APERTE TORRI
    for (x = 1; x <= 8; x++)
    {
        string stringa_di_comodo = "";
        for (y = 1; y <= 8; y++)
        {
            stringa_di_comodo ~= board[x][y];
        }
        if (count(stringa_di_comodo, "R") == 1 && count(stringa_di_comodo, "-") == 7) // Es: "R------"
            v += 5;
        if (count(stringa_di_comodo, "r") == 1 && count(stringa_di_comodo, "-") == 7) // Es: "r------"
            v -= 5;
    }

    //------------------Bonus TORRI IN SETTIMA
    for (x = 1; x <= 8; x++)
    {
        if (board[x][7] == 'R')
            v += 5;
        //------------------------
        if (board[x][2] == 'r')
            v -= 5;
    }

    //--------------------Penalizza le mosse che mettono IN PRESA i propri pezzi-----------
    if (chi_ha_eseguito_ultima_mossa == "bianco")
    {
        if (pezzo_sotto_scacco(board, 'Q') == 1)
            v -= 8;
        if (pezzo_sotto_scacco(board, 'R') == 1)
            v -= 7;
        if (pezzo_sotto_scacco(board, 'B') == 1)
            v -= 6;
        if (pezzo_sotto_scacco(board, 'N') == 1)
            v -= 5;
        if (pezzo_sotto_scacco(board, 'P') == 1)
            v -= 4;
    }
    if (chi_ha_eseguito_ultima_mossa == "nero")
    {
        if (pezzo_sotto_scacco(board, 'q') == 1)
            v += 8;
        if (pezzo_sotto_scacco(board, 'r') == 1)
            v += 7;
        if (pezzo_sotto_scacco(board, 'b') == 1)
            v += 6;
        if (pezzo_sotto_scacco(board, 'n') == 1)
            v += 5;
        if (pezzo_sotto_scacco(board, 'p') == 1)
            v += 4;
    }

    //--------------------Bonus per le mosse che mettono IN PRESA i pezzi avversari-----------
    if (chi_ha_eseguito_ultima_mossa == "bianco")
    {
        if (pezzo_sotto_scacco(board, 'k') == 1)
            v += 6;
        if (pezzo_sotto_scacco(board, 'q') == 1)
            v += 5;
        if (pezzo_sotto_scacco(board, 'r') == 1)
            v += 4;
        if (pezzo_sotto_scacco(board, 'b') == 1)
            v += 3;
        if (pezzo_sotto_scacco(board, 'n') == 1)
            v += 2;
        if (pezzo_sotto_scacco(board, 'p') == 1)
            v += 1;
    }
    if (chi_ha_eseguito_ultima_mossa == "nero")
    {
        if (pezzo_sotto_scacco(board, 'K') == 1)
            v -= 6;
        if (pezzo_sotto_scacco(board, 'Q') == 1)
            v -= 5;
        if (pezzo_sotto_scacco(board, 'R') == 1)
            v -= 4;
        if (pezzo_sotto_scacco(board, 'B') == 1)
            v -= 3;
        if (pezzo_sotto_scacco(board, 'N') == 1)
            v -= 2;
        if (pezzo_sotto_scacco(board, 'P') == 1)
            v -= 1;
    }

    //--------------------MALUS distanza dei pezzi dal RE avversario-----------
    byte posizione_re_x, posizione_re_y;
    byte distanza;
    int somma = 0;
    byte elementi = 0;
    int media;

    if (chi_ha_eseguito_ultima_mossa == "bianco") // Tocca al NERO
    {

        for (y = 8; y >= 1; y--)
        { //-----Cerca il Re NERO
            for (x = 1; x <= 8; x++)
            {
                if (board[x][y] == 'k')
                {
                    posizione_re_x = x;
                    posizione_re_y = y;
                }
            }
        }
        somma = 0;
        elementi = 1; // (non 0), per evitare la Division by 0 (il re puo' sparire dalla scacchiera)
        for (y = 8; y >= 1; y--)
        { //-----Cerca i Pezzi BIANCHI
            for (x = 1; x <= 8; x++)
            {
                if (indexOf("KQRBNP", board[x][y]) >= 0)
                {
                    distanza = cast(byte)((posizione_re_x - x) ^^ 2 + (posizione_re_y - y) ^^ 2);
                    somma += distanza;
                    elementi++;
                }
            }
        }
        media = somma / elementi;
        media = media / 5; //-----------------Riduzione valore
        v += media;

    }

    if (chi_ha_eseguito_ultima_mossa == "nero") // Tocca al BIANCO
    {

        for (y = 8; y >= 1; y--)
        { //-----Cerca il Re BIANCO
            for (x = 1; x <= 8; x++)
            {
                if (board[x][y] == 'K')
                {
                    posizione_re_x = x;
                    posizione_re_y = y;
                }
            }
        }
        somma = 0;
        elementi = 1; // (non 0), per evitare la Division by 0 (il re puo' sparire dalla scacchiera);

        for (y = 8; y >= 1; y--)
        { //-----Cerca i Pezzi NERI
            for (x = 1; x <= 8; x++)
            {
                if (indexOf("kqrbnp", board[x][y]) >= 0)
                {
                    distanza = cast(byte)((posizione_re_x - x) ^^ 2 + (posizione_re_y - y) ^^ 2);
                    somma += distanza;
                    elementi++;

                }
            }
        }

        media = somma / elementi;
        media = media / 5; //-----------------Riduzione valore
        v -= media;

    }

    return v;
}

//===============================================================================
// La funzione riceve un ARRAY ASSOCIATIVO di stringhe (le linee) con un valore INT. es:
// e2e4 e7e5 g1f3 b8c6 0.2

string minimax(int[string] linee_ricevute, string colore_ultimo_nodo)
{

    int record_mondiale;
    string best_move;
    int caso;

    //----------------------Prova a liberare memoria RAM -----------
    GC.free(tabella_minimax.ptr);
    GC.minimize;
    GC.collect;
    tabella_minimax = null;
    //----------------------Prova a liberare memoria RAM -----------
    GC.free(array_stringa_linee.ptr);
    GC.minimize;
    GC.collect;
    array_stringa_linee = null;

    //--------Crea un unico array stringa con CHIAVE e VALORE. Serve per il SORT Es: "e2e4 e7e5 g1f3 b8c6 0.2"
    foreach (k, v; linee_ricevute)
    {
        array_stringa_linee ~= k ~ to!string(v);
    }
    array_stringa_linee.sort();
    //--------------Riempie una matrice di mosse e di valutazioni------------------
    // Esempio: ["a3a2", "0", "a8a7", "0", "a2a1", "0", "d7b5", "-1"]
    // Esempio: ["a3a2", "0", "a8a7", "0", "a2a3", "0", "b7b6", "-1"]
    // Esempio: ["a3a2", "0", "a8a7", "0", "a2a3", "0", "d7a4", "-1"]
    // Esempio: ["a3a2", "0", "a8a7", "0", "a2a3", "0", "d7c6", "-1"]
    // Esempio: ["a3a2", "0", "a8a7", "0", "a2a3", "0", "e7e5", "-1"]

    foreach (k; array_stringa_linee)
    {
        string[] elem = split(k, " ");
        string[] singolo_record = [elem[0], "0", elem[1], "0", elem[2], "0", elem[3], elem[4]];
        tabella_minimax ~= singolo_record;
    }
    tabella_minimax ~= ["xxxx", "0", "xxxx", "0", "xxxx", "0", "xxxx", "0"];

    int inizio, fine;

    //------------Processa livello (vede i livelli a ritroso, dalle foglie alla radice)---------
    for (int i = 4; i >= 0; i = i - 2)
    {
        inizio = 0;
        fine = 0;
        while (1)
        {
            //--------------Cerca il GRUPPO di mosse uguali, stabilendo inizio e fine in ARRAY-----
            string mossa_da_considerare = tabella_minimax[inizio][i];
            for (int k = inizio; k <= 999999999; k++)
            {
                if (tabella_minimax[k][i] != mossa_da_considerare)
                {
                    fine = k - 1;
                    break;
                }
            }
            //-----------------Decide se MIN o MAX-----------
            if (colore_ultimo_nodo == "nero" && (i / 2) % 2 == 0)
            {
                record_mondiale = 999999;
                for (int k = inizio; k <= fine; k++)
                {
                    if (to!int(tabella_minimax[k][i + 3]) < record_mondiale)
                    {
                        record_mondiale = to!int(tabella_minimax[k][i + 3]);
                    }
                }
            }
            //-----------------Decide se MIN o MAX-----------
            if (colore_ultimo_nodo == "nero" && (i / 2) % 2 == 1)
            {
                record_mondiale = -999999;
                for (int k = inizio; k <= fine; k++)
                {
                    if (to!int(tabella_minimax[k][i + 3]) > record_mondiale)
                    {
                        record_mondiale = to!int(tabella_minimax[k][i + 3]);
                    }
                }
            }
            //-----------------Decide se MIN o MAX-----------
            if (colore_ultimo_nodo == "bianco" && (i / 2) % 2 == 0)
            {
                record_mondiale = -999999;
                for (int k = inizio; k <= fine; k++)
                {
                    if (to!int(tabella_minimax[k][i + 3]) > record_mondiale)
                    {
                        record_mondiale = to!int(tabella_minimax[k][i + 3]);
                    }
                }
            }
            //-----------------Decide se MIN o MAX-----------
            if (colore_ultimo_nodo == "bianco" && (i / 2) % 2 == 1)
            {
                record_mondiale = 999999;
                for (int k = inizio; k <= fine; k++)
                {
                    if (to!int(tabella_minimax[k][i + 3]) < record_mondiale)
                    {
                        record_mondiale = to!int(tabella_minimax[k][i + 3]);
                    }
                }
            }
            //-------------RIMPIAZZA-----
            for (int k = inizio; k <= fine; k++)
            {
                tabella_minimax[k][i + 1] = to!string(record_mondiale);
            }

            inizio = fine + 1;

            if (inizio == tabella_minimax[].length - 1)
                break;
        }
    }

  
    //----------------------Decide se e' MATTO o STALLO----------------------------
    for (int k = 0; k < tabella_minimax[].length - 1; k++) // Non considera L'ULTIMO RECORD
    {
        if (tabella_minimax[k][2] == "STAL" && A_CHI_TOCCA == "bianco")
            tabella_minimax[k][1] = to!string(-999998);
        if (tabella_minimax[k][2] == "STAL" && A_CHI_TOCCA == "nero")
            tabella_minimax[k][1] = to!string(999998);
        if (tabella_minimax[k][2] == "MATT" && A_CHI_TOCCA == "bianco")
            tabella_minimax[k][1] = to!string(999997);
        if (tabella_minimax[k][2] == "MATT" && A_CHI_TOCCA == "nero")
            tabella_minimax[k][1] = to!string(-999997);
    }




    //----------------------Restituisce la MIGLIORE MOSSA del BIANCO (valore MAGGIORE)----------------------------
    if (A_CHI_TOCCA == "bianco")
    {
        record_mondiale = -999999;
        //--------Trova la migliore valutazione----
        for (int k = 0; k < tabella_minimax[].length - 1; k++)
        { // Non considera L'ULTIMO RECORD
            if (to!int(tabella_minimax[k][1]) > record_mondiale)
            {
                record_mondiale = to!int(tabella_minimax[k][1]);
            }
        }
        while (1)
        {
            caso = uniform(0, tabella_minimax[].length - 1);
            if (to!int(tabella_minimax[caso][1]) == record_mondiale)
                break;
        }
        best_move = tabella_minimax[caso][0];
    }
    //----------------------Restituisce la MIGLIORE MOSSA del NERO(valore MINORE)----------------------------
    if (A_CHI_TOCCA == "nero")
    {
        record_mondiale = 999999;
        //--------Trova la migliore valutazione----
        for (int k = 0; k < tabella_minimax[].length - 1; k++)
        { // Non considera L'ULTIMO RECORD
            if (to!int(tabella_minimax[k][1]) < record_mondiale)
            {
                record_mondiale = to!int(tabella_minimax[k][1]);
            }
        }
    }





    //--------------------------Sceglie a caso la MIGLIORE mossa------
    while (1)
    {
        caso = uniform(0, tabella_minimax[].length - 1);
        if (to!int(tabella_minimax[caso][1]) == record_mondiale)
            break;
    }
    best_move = tabella_minimax[caso][0];


    //--------------------------Salva il LOG MINI MAX------
    if (LOGMINMAX == true)
    {
        File file = File("minimax.txt", "w");
        foreach (k; tabella_minimax)
        {
            file.writeln(k);
        }
        file.close();
    }


    //---------------------

    return best_move;
}
