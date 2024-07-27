Merge multiple CSV files into one, using the specified headers and correcting the invoice data.

BASH Functionality:
1. Asks the user for the invoice CSV file path and the output file name.
2. Shows available CSV files in the current directory, excluding the invoice file.
3. Lets the user choose other CSV files to combine with the invoice file.
4. Uses a default headers file or lets the user specify a different one.
5. Copies headers to a temporary file, prepares arguments, and runs a Python script to combine the CSV files.
6. Deletes the temporary headers file and converts the output file to ASCII.
7. Tells the user that the output file has been saved successfully.