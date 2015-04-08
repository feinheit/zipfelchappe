.. _usage:

Using the app
=============

Adding the fundraising module to your website
---------------------------------------------

In the Dajngo admin interface, create a new page. Add an application content and select "Zipfelchappe projects".

If you have a multilingual website, you have to do this for every language.


Adding project teasers
----------------------

There are two content types which let you promote selected projects on a web page.
``ProjectTeaserContent`` which promotes a single project and ``ProjectTeaserRowContent`` to promote three projects.

To make those available in the admin interface, register them with the ``Page`` module::

    from zipfelchappe.content import ProjectTeaserContent, ProjectTeaserRowContent

    Page.create_content_type(ProjectTeaserContent, regions=('main',))
    Page.create_content_type(ProjectTeaserRowContent, regions=('main',))

You have to migrate your database after adding the content types.
Once the content types are registered, you can select them in the admin interface.

They use the template ``zipfelchappe/project_teaser.html`` and ``zipfelchappe/project_teaser_row.html`` respectively.
