.. _postfinance:

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
Postfinance bietet einen UTF-8 Endpoint unter der URL
https://e-payment.postfinance.ch/ncol/test/orderstandard_utf8.asp an.
Die SHA-1 Signierung auf Postfinance-Seite wird allerdings weiterhin mit Latin-1 Encoding
ausgeführt. Daher kann es passieren, dass der Hash des Callbacks ungültig ist.
Aus diesem Grund wird der Standard-Endpoint verwendet.
