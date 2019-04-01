Logging In
----------

Privileged tasks in CRDS such as:

1. Submitting new files
2. Managing the context

require authenticating with the CRDS server.

Authentication Overview
.......................

Logging in requires what can be a multi-step workflow.  The steps of logging in
are:

1. Instrument selection  (Pipeline operators select "none")
2. MyST authentication  (skipped if done previously)
3. Auth.mast token authorization (skipped if done previously)
4. CRDS server account verification  (hidden unless fails)
5. Instrument locking (hidden unless fails)

In addition to basic MyST and auth.mast authentication,  CRDS adds
the requirement that you have a CRDS account and that you lock any
instrument for which you are submitting files.

Instrument Selection
....................

The first step of logging in is to select the instrument for which you will be
submitting files.  Eventually during login, CRDS will lock this instrument so
that you have exclusive access for one submission.  If a lock cannnot be
obtained because someone else has it, your login will fail.  This prevents your
changes from colliding with another's in CRDS and the loss of work.

.. figure:: images/web_login.png
   :scale: 50 %
   :alt: login page with instrument locking

MyST Authentication
...................

The outer-most layer of CRDS authentication is to authenticate with MyST.  This
proves to CRDS that you're participating with STScI in a general way.  This
step requires entry of your e-mail or username and AD password and may also
entail related two factor authorization not shown.

.. figure:: images/myst_login.png
   :scale: 50 %
   :alt: MyST authentication

Auth.mast Authorization 
....................... 

auth.mast may request that you authorize CRDS to obtain a token.  These
tokens are the way in which CRDS obtains your MyST identity.

.. figure:: images/auth_mast_login.png
   :scale: 50 %
   :alt: auth.mast page asking to grant token to CRDS

CRDS Account
............

As part of submitting files or managing the CRDS context, you need to apply for
a CRDS account.  These permissions are checked automatically after your MyST
identity is verified.

**IMPORTANT** Your MyST identity is connected to your CRDS permissions via your
MyST e-mail.  You should specify your MyST e-mail when applying for a CRDS
account.

CRDS Instrument Locking
.......................

When a user logs in, the instrument they've locked and the time remaining on
the lock are displayed next to the home button:

.. figure:: images/web_logged_in.png
   :scale: 50 %
   :alt: logged in page with count down timer

Instrument locking is used to prevent conflicting modifications to the same
CRDS rules files by simultaneous files submissions.

Other users who attempt to login for the same instrument while it is locked
will be denied.   When the lock holder confirms or cancels their submission,'
the lock is released so that others can proceed.

When the user performs an action on the website, their lock timer is reset to
its maximum value.

If your lock times out, another user can take the lock and submit files to the
same instrument and reference type.  Different instruments or reftypes should
not cause conflicts.  Submitting to the same instrument and reftype will
generally cause the first set of conflicting rules changes to be lost.

Forced submissions should be carefully coordinated since by definition locking
protections are not in place.

Care should be taken with the locking mechanism and file submissions.  **DO NOT**:

* Don't login from multiple browsers or sites.  The last browser/site you log
  in from will steal the lock from the original login.  While this won't abort
  any submission, it will open the possibility for conflict and require earlier
  submissions waiting for confirmation to be *forced*.

* You cannot login for more than one instrument at a time.  

* Don't perform multiple file submissions for the same instrument at the same
  time.  Finish and confirm or cancel each file submission before proceeding
  with the next.

