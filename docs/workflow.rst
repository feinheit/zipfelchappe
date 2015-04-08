.. _workflow:

Crowdfunding workflow
=====================

User roles
----------

- Platform owner: Owns and operates the platform (website).
- Project owner: Created a project featured on the platform. The project owner receives the funds on
  successful completion of the project.
- Visitor: A visitor to the website.
- Backer: A visitor who has backed a project becomes a backer.


Project setup
-------------

#. A project owner creates an account on the plattform.
#. He creates a project.
#. The platform owner reviews and approves the project.
#. The project is open for bidding.

Bidding phase
-------------

#. A visitor visits the website and looks at the project.
#. He decides to support it by clicking on the 'Back this project' button.
#. He is redirected to the backing page. On this page he has to enter the amount he wishes to back
   and select the reward.
#. He gets redirected to the payment provider site where he enter his payment details.
#. After successful completion he gets redirected to the thank you page
   which is the project detail page with 'thank_you' and the pledge id added as a query string.
   He is now a backer.
   If the visitor cancels the payment he is redirected to the detail page again. A message informs him
   that he had cancelled the transfer.

End phase
---------

#. After the project end date has passed, the bidding has ended.
#. The system sends out a message to all backers informing them if the funding has succeeded or not.
#. If the project did not succeed, the preapprovals are cancelled. No money is deducted.
#. If the project did succeed, the money is transferred to the project owner.

