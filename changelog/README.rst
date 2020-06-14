This directory contains "newsfragments" which are short files that contain a small **ReST**-formatted
text that will be added to the next ``CHANGELOG``.

The ``CHANGELOG`` will be read by users, so this description should be aimed to w1thermsensor users
instead of describing internal changes which are only relevant to the developers.

Make sure to use complete sentences with correct case and punctuation, for example::

    Fix issue with non-ascii messages from the ``warnings`` module.

Each file should be named like ``<ISSUE>.<TYPE>``, where
``<ISSUE>`` is an issue number, and ``<TYPE>`` is one of:

* ``feature``: new user facing features, like new command-line options and new behavior.
* ``bugfix``: fixes a reported bug.
* ``doc``: documentation improvement, like rewording an entire session or adding missing docs.
* ``removal``: feature removal.

So for example: ``123.feature``, ``456.bugfix``.

If your PR fixes an issue, use that number here. If there is no issue,
then after you submit the PR and get the PR number you can add a
changelog using that instead.

If you are not sure what issue type to use, don't hesitate to ask in your PR.

``towncrier`` preserves multiple paragraphs and formatting (code blocks, lists, and so on), but for entries
other than ``features`` it is usually better to stick to a single paragraph to keep it concise.
You can install ``towncrier`` and then run ``towncrier --draft``
if you want to get a preview of how your change will look in the final release notes.

Disclaimer: this README was copied and adapted to the needs of w1thermsensor from the awesome pytest project.
