
.. _payment_provider:

Payment provider
================


Paypal
------

This provider uses paypals Adaptive Payments API. Documentation can be found
`here <https://www.x.com/developers/paypal/documentation-tools/adaptive-payments/>`_.

To start developing, log on to https://developer.paypal.com and follow the steps
there to get a sandbox testing account.

Once you want to go live you need to submit your application to http://x.com.
This process requires a lot of infos and may take some time. You need to have
your site already online and working on the sandbox before you should submit
to x.com



Postfinance
-----------

Postfinance is not a classical crowdfunding payment provider but very common in
Switzerland. You find their offers https://www.postfinance.ch/en/biz/prod/eserv/epay.html

When you configure this provider, make sure that:

* Default operation mode ist "Authorisation"
* SHA-1 is the active hash algorithm
* You have set the correct SHA1-IN and SHA1-OUT hashes in your settings
* The Direct HTTP server-to-server urls point to the providers IPN view
* The request method for IPN messages is POST


If you want to automatically request payments for successfully funded projects
in the background, you will need to purchase the optional "DirectLink" package
by postfinance. This is available on the Basic and the Professional plan.


Custom
------

If you want to implement a custom payment provider, you need to follow a few
quick rules:

* Provide a 'zipfelchappe_<providername>_payment' named view to you start
  the payment process. You can get the pledge to pay from the session

* If the payment has been authorized, set the pledge status to AUTHORIZED and
  redirect to the 'zipfelchappe_pledge_thankyou' view.

* If payment was canceled, redirect to the 'zipfelchappe_pledge_canceled' view

* When payment is collected, set pledge status to PAID

* If payment failed multiple times, set pledge status to FAILED


Take a look at the exisiting payment providers to get further insights.
