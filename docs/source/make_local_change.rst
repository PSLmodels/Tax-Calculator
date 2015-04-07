Making changes in your local tax-calculator directory
======================================================

Example 1. Update a tax parameter’s description
------------------------------------------------

In this example, I make a simple change in the file that stores the Tax Calculator’s tax parameters. The procedures I outline below are similar to the steps you’ll take when you make changes in your own local tax-calculator directory.

**1. Navigate to the file that I want to edit and open it.**

   I store my local repo in my projects folder on my Home directory. The tax parameters are in the file ~/projects/tax-calculator/taxcalc/params.json.

**2. Identify what I want to change.**

   Users may not be familiar with the acronyms AMTI and AMT used in the description of the Alternative Minimum Tax (AMT) exemption amount parameter. I want to include their full names in addition to the acronyms in the description that is highlighted below.

   .. image:: /screen-shot-1.png

..
**3. Make my changes and save.**

   I add the written-out forms of AMTI and AMT and save my changes. The new code looks like this:

   .. image:: /screen-shot-2.png

..

**4. Return to the** :doc:`Contributor Guide </contributor_guide>` **and continue with Step 4 of the Workflow section.**

   Now that I’ve successfully made my changes, it’s time to move on with testing.


.. _`Workflow`: http://taxcalc.readthedocs.org/en/latest/contributor_guide.html#workflow
