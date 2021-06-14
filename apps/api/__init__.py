'''

Quart-based API utilizing an AsyncPG back-end database
Record Queries and Modifications Only!
Processing should be done using the client package.

Packages:
    Messaging (Modmail, Guild-Based)
    Statistics (Guild and User-Based)
    Tasks/Reminders (Post-Completion)
    Experience (Global and Guild-Based)
    Infractions (Global and Guild-Based)
    Social/Creator Profiles (User-Based)
    Custom Commands (Global and Guild-Based)

Authentication:

    URL         "key"               secrets.token_urlsafe(24)
    Header      "client-id"         Sourced from Discord Bot ID
    Header      "client-secret"     [secrets.choice(12)].[secrets.token_urlsafe(12)]

    Storage
        - Application ID    Raw             "client-id"
        - Salt Protocol     Raw             4 character strings containing uniquely "a", "b", "c" or "d", separated by 2 "-" and a "."
        - Access Token      SHA-256 Hex     Depending on your Salt Protocol, this is the Hex Digested Hash of the string created by salting data

            Salt Protocol:
                - 4 character string containing "a" indicates the "key" parameter
                - 4 character string containing "b" indicates the "client-secret"[0] parameter
                - 4 character string containing "c" indicates the "client-id" parameter
                - 4 character string containing "d" indicates the "client-secret"[1] parameter

                Example:
                    ID:         654887208603615263
                    Key:        SiqSKt-7lxbdgOwhyi___fTE7Xp49cax
                    Secret:     c2H5SGIJ9bsJ.Ua541AGPcM8UzpEA

                    Protocol:   "az0y.q7eb-nc9g-0dk1"
                    Raw Token:  SiqSKt-7lxbdgOwhyi___fTE7Xp49cax.c2H5SGIJ9bsJ-654887208603615263-Ua541AGPcM8UzpEA
                    Stored:     7a953b14ba4e5315526fdff815c3a2073ab850aea65917f2805f4f2d475324f9

        User Credentials:
            - Username: Application ID
            - Password: Raw Token

        Once the provided credentials have been verified using the Authentication API, the request will automatically
        be redirected and attempt to connect to the main database using the new login (see "User Credentials" above)


'''
