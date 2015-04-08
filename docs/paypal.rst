.. _paypal:

PayPal
======

Please read the `PayPal Crowdfunding Application Guidelines`_ for informations and guidelines.

Some important facts when using Paypal as a payment provider:

 - The platform owner needs to be a registered business and have a PayPal Business account.

 - You have to use `Adaptive Payments`_ for crowdfunding projects.

 - Rewards are limited to a value of $100 USD.

 - The platform needs to be approved by Paypal.

There are two payment flows: parallel and chained. With parallel payment, all parties
(the project owner and the platform owner) get their funds at the same time. They share the paypal fees.
With chained payments the funds are transferred to the project owner's account first and from there payments
are distributed to other involved parties. The project owner pays the Paypal fees.
To force a chained payment, add the property `'primary': 'true'` to the primary receiver in the
`ZIPFELCHAPPE_PAYPAL.RECEIVERS` list.


Testing
-------
Paypal offers a Sandbox_ for testing the Classic API.
When creating your PayPal developer account, consider creating an account that you don’t mind
sharing with others on your development team.
This way, you can share your Sandbox test accounts without compromising the security
of your personal PayPal account.


Going Live
----------
To obtain live PayPal credentials, you must have a verified Premier or verified Business PayPal account.
Please read the `Going Live guide`_.

The `PayPal Developer agreement`_ highlights all the points with which your application must comply.
Be sure to read and fully understand this document before submitting your application to PayPal
for review.


.. _`PayPal Crowdfunding Application Guidelines`: https://developer.paypal.com/docs/classic/lifecycle/crowdfunding/
.. _`Adaptive Payments`: https://developer.paypal.com/docs/classic/adaptive-payments/integration-guide/APIntro/
.. _Sandbox: https://developer.paypal.com/docs/classic/lifecycle/ug_sandbox/
.. _`Going Live guide`: https://developer.paypal.com/docs/classic/lifecycle/goingLive/
.. _`PayPal Developer agreement`: https://www.paypal.com/us/webapps/mpp/ua/xdeveloper-full
