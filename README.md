# sql_completion
Website with experimentation material: https://marielgy.github.io/sql_experimentation/

## Test the interface :
  run ```python demo.py``` for interface with completion
  run ```python demo_symple.py``` for only sql
  
## Notes on completion :
   * You can only complete a valid SQL query
   * You can select the number of completion to obtain
   * Simple query to test : 
   ```sql
   Select * from Packages
   ```
   
## Database was created as follows:
  ```sql
  CREATE TABLE Cities(
                city_ID DECIMAL,
                distance DECIMAL,
                PRIMARY KEY (city_ID)
            )
            
  CREATE TABLE Packages(
            package_ID DECIMAL,
            destination DECIMAL,
            length DECIMAL,
            width DECIMAL,
            height DECIMAL,
            weight DECIMAL,
            price DECIMAL,
            PRIMARY KEY (package_ID)
            FOREIGN KEY (destination) references Cities(city_ID)
        )
  ```
  
  ## Re-using completion:
  To use the completion in a new program, you need the 
  ```python 
  completeQuery(datasetQuery, database, maxcompletions)
  ``` 
  function from th```algoAI.py``` file.
  
  It requires :
   * The query to complete
   * The database on which the query is evaluated
   * The number of completions to obtain
  
