system plików: W pliku na dysku należy zorganizować system plików z wielopoziomowym katalogiem. Należy zrealizować aplikację konsolową, przyjmującą polecenia, wywoływaną z nazwą pliku implementującego dysk wirtualny. Należy zaimplementować następujące operacje, dostępne dla użytkownika tej aplikacji:
1. Tworzenie wirtualnego dysku (gdy plik wirtualnego dysku będący parametrem nie istnieje to pytamy się o utworzenie przed przejściem do interakcji) - jak odpowiedź negatywna to kończymy program. Parametrem polecenia powinien być rozmiar tworzonego systemu plików w bajtach. Dopuszcza się utworzenie systemu nieznacznie większego lub mniejszego, gdy wynika to z przyjętych założeń dotyczących budowy.
2. Kopiowanie pliku z dysku systemu na dysk wirtualny
3. Utworzenie katalogu na dysku wirtualnym
4. Usunięcie katalogu z dysku wirtualnego
5. Kopiowanie pliku z dysku wirtualnego na dysk systemu,
6. Wyświetlanie katalogu dysku wirtualnego z informacją o rozmiarze (sumie) plików w katalogu, rozmiarze plików w katalogu razem z podkatalogami (suma), oraz ilości wolnej pamięci na dysku wirtualnym
7. Tworzenie twardego dowiązania do pliku lub katalogu
8. Usuwanie pliku lub dowiązania z wirtualnego dysku
9. Dodanie do pliku o zadanej nazwie n bajtów
10. Skrócenie pliku o zadanej nazwie o n bajtów
11. Wyświetlenie informacji o zajętości dysku