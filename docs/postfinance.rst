Postfinance
===========

Login-URL für Produktion: https://e-payment.postfinance.ch/Ncol/Prod/BackOffice/Login
Login-URL für Test: https://e-payment.postfinance.ch/Ncol/Test/BackOffice/login/index

SHA-IN Signatur ist unter
Konfiguration/Technische Informationen/Daten- und Urspungsüb..
https://e-payment.postfinance.ch/Ncol/Test/BackOffice/technicalinformation/dataandoriginverification

SHA-OUT Signatur und URLS:
Konfiguration/Technische Informationen/Tansaktions-Feedback
https://e-payment.postfinance.ch/Ncol/Test/BackOffice/technicalinformation/transactionfeedback

Die Parameter bei den Fehlerseiten können im Postfinance-Admin aktiviert werden.

Eine bestätigte Zahlung muss innerhalb von 30 Tagen abgebucht werden.
Danach wird sie anulliert.


Text-Encoding
-------------

Standardmässig ist bei Postfinance das Text-Encoding latin-1.
Zipfelchappe verwendet den UTF8-Endpoint:
https://e-payment.postfinance.ch/ncol/test/orderstandard_utf8.asp. Bei Latin-1 encodierung muss
der Standard-Endpoint https://e-payment.postfinance.ch/ncol/test/orderstandard.asp
verwendet werden.
