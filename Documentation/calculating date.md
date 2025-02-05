### Seconds to Days:

Divide the total seconds by 86400 (seconds per day).
Quotient = Days since epoch.
Remainder = Remaining seconds (use this for later calculations).

### Approximate Year:

1. Divide the days since epoch by 365.25 (use integer division; the fractional part is discarded). This is your approximate year offset from 1970.
2. Add this offset to 1970. This is your approximate year.

### Refine Year (Integer Version):

1. Calculate the number of days from January 1, 1970, to January 1 of the approximate year. Use a loop, adding 365 for regular years and 366 for leap years (divisible by 4, but not by 100, unless also divisible by 400).
2. Compare this calculated number of days with the days since the epoch.
3. If the days since the epoch are greater or equal, increment the approximate year and repeat the comparison.
4. If the days since the epoch are less, decrement the approximate year and repeat the comparison.
5. When the calculated days are close to the days since the epoch, you have your year.

### Days in Current Year:

Calculate the number of days from January 1 of the correct year to the current date (using the remaining days from step 1). Again, use a loop and account for leap years.

### Month:

1. Start with January (month 1).
2. Subtract the number of days in the current month from the remaining days.
3. If the result is greater than or equal to zero, increment the month and repeat.
4. When the result becomes negative, the previous month is the correct month. Add back the number of days for the last incremented month to the remaining days.
5. 
### Day:

Add 1 to the remaining days (from the month calculation). This is the day of the month.

### Hour:

1. Divide the remaining seconds (from step 1) by 3600 (seconds per hour).
2. Quotient = Hour.
3. Remainder = Remaining seconds.

### Minute:

1. Divide the remaining seconds by 60 (seconds per minute).
2. Quotient = Minute.
3. Remainder = Remaining seconds.

### Second:

1. The remaining seconds are the seconds.
