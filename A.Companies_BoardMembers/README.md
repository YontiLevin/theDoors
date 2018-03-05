# Corporates -> Senior positions 

We want to create a list of the top positions in big Israeli corporates.  
Work plan:  
1. Retrieve links to public companies reports from [Maya](http://maya.tase.co.il)   
   >The TASE Corporate Actions Systems (MAYA) provides a view of corporate events and income payments dates including: dividend, interest rate, exercise dates, general assembly schedule and more.
2. From each link extract relevant information
    - company name
    - position info
        - person info
        - start/end date
        - etc...

3. Save all to CorporatePositions database

---

### Usage

#### 1. Run a splash docker  
[splash](https://github.com/scrapinghub/splash) is a javascript rendering service with an HTTP API.  
We will need it for scraping Maya.  

**Installation and More...**  
please refer to its [docs](https://splash.readthedocs.io/).

**Run**  
```docker run -d -p 8050:8050 -p 5023:5023 scrapinghub/splash ```

#### 2. Run app.py  
```python app.py```

