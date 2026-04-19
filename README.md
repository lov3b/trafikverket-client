# Trafikverket Client

En inofficiel klient för Trafikverkets webbapi.
För närvarande stöds endast [https://fp.trafikverket.se](fp.trafikverket.se),
men jag är öppen för att lägga till fler subsidor och så vidare.

## Kom igång

Börja med att installera paketet.
Följande installerar klienten med stöd för att rendrera qr-koden till terminalen.

```bash
pip3 install "trafikverket-client[qr]"
```

## Vägkarta

- [x] Logga in med BankID
  - [x] Logga in med auto-start-token ("öppna på samma enhet")
  - [x] Logga in med QR-kod
- [x] Se tider tillgängliga för examination
- [x] Se bokade tider
- [x] Se behörighet
- [ ] Boka en examination


## Juridiskt

Detta projekt är ett inofficiellt klientbibliotek och har ingen koppling till, är inte godkänt av och sponsras inte av Trafikverket eller BankID.

"Trafikverket" och "BankID" är varumärken som tillhör sina respektive innehavare. Projektet tillhandahålls för interoperabilitet, utbildningssyften och personligt bruk.

Du ansvarar själv för att användningen av programvaran följer tillämpliga lagar, regler och eventuella användarvillkor för de tjänster som används.

Programvaran tillhandahålls i befintligt skick, utan några uttryckliga eller underförstådda garantier. Användning sker på egen risk.
