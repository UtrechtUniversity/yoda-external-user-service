The following files should be provided for e-mails to work:

(examples are provided in the example directory)

invitation.txt            - sent to external users
invitation-sent.txt       - sent to group managers
activation-succesful.txt  - sent to external users
invitation-accepted.txt   - sent to group managers

To enable HTML mails, provide '.html' versions of the above e-mails *in
addition to* the .txt versions (you always need a plaintext version).

Also, the following files are required for all HTML mails and are implicitly
included at the start and end of the mail body. These files must be provided if
a HTML version exists for *any* of the above e-mail templates.

common-end.html
common-start.html

Within both TXT and HTML e-mail templates, certain variable names can be used,
depending on the template name:

- invitation
    - [[USERNAME]] (the external user name)
    - [[CREATOR]]  (the group manager user name)
    - [[HASH_URL]] (the activation URL, including a random hash)
- invitation-sent
    - [[USERNAME]]
    - [[CREATOR]]
- invitation-accepted
    - [[USERNAME]]
    - [[CREATOR]]
- activation-succesful
    - [[USERNAME]]

All occurrences of these variables will be replaced with their respective values.
The names must match exactly, including the square brackets.
