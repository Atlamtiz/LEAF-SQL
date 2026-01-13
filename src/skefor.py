prompt_base_phase = """You are a SQL expert. Your task is to generate a set of potential Base SQL skeletons based on the user's question and the database schema. A Base skeleton includes only the top-level clauses like SELECT, FROM, WHERE, GROUP BY, ORDER BY, and set operators like INTERSECT, UNION, EXCEPT. Do not include any specific columns, values, or subqueries. 

Here are 3 input-output demonstrations you can refer to:
============================ demonstration 1 ============================
 【Database Schema】
【DB_ID】 movie_platform
【Schema】
# Table: movies
[
(movie_id:INTEGER, Primary Key, Examples: [1, 2, 3]),
(movie_title:TEXT, Examples: [La Antena, Elementary Particles, It's Winter]),
(movie_release_year:INTEGER, Examples: [2007, 2006, 2005]),
(movie_url:TEXT),
(movie_title_language:TEXT, Examples: [en]),
(movie_popularity:INTEGER, Examples: [105, 23, 21]),
(movie_image_url:TEXT),
(director_id:TEXT, Examples: [131, 73, 82]),
(director_name:TEXT, Examples: [Esteban Sapir, Oskar Roehler, Rafi Pitts]),
(director_url:TEXT)
]
# Table: ratings
[
(movie_id:INTEGER, Examples: [1066, 1067, 1068]),
(rating_id:INTEGER, Examples: [15610495, 10704606, 10177114]),
(rating_url:TEXT),
(rating_score:INTEGER, Examples: [3, 2, 4]),
(rating_timestamp_utc:TEXT, Examples: [2017-06-10 12:38:33, 2014-08-15 23:42:31, 2014-01-30 13:21:57]),
(critic:TEXT),
(critic_likes:INTEGER, Examples: [0, 1, 2]),
(critic_comments:INTEGER, Examples: [0, 2, 1]),
(user_id:INTEGER, Examples: [41579158, 85981819, 4208563]),
(user_trialist:INTEGER, Examples: [0, 1]),
(user_subscriber:INTEGER, Examples: [0, 1]),
(user_eligible_for_trial:INTEGER, Examples: [1, 0]),
(user_has_payment_method:INTEGER, Examples: [0, 1])
]
# Table: ratings_users
[
(user_id:INTEGER, Examples: [41579158, 68654088, 84114365]),
(rating_date_utc:TEXT, Examples: [2017-06-10, 2012-10-02, 2010-12-25]),
(user_trialist:INTEGER, Examples: [0, 1]),
(user_subscriber:INTEGER, Examples: [0, 1]),
(user_avatar_image_url:TEXT),
(user_cover_image_url:TEXT),
(user_eligible_for_trial:INTEGER, Examples: [1, 0]),
(user_has_payment_method:INTEGER, Examples: [0, 1])
]
【Foreign keys】
lists.user_id=lists_users.user_id, lists_users.user_id=ratings_users.user_id, lists.list_id=lists_users.list_id, ratings.user_id=ratings_users.user_id, lists_users.user_id=ratings.user_id, movies.movie_id=ratings.movie_id

 【Question】
List all movies with the best rating score. State the movie title and number of Mubi user who loves the movie.

Based on the question and schema, generate up to {m} diverse Base skeletons that represent plausible high-level structures for the query.
```sql skeleton
"SELECT _ FROM _ WHERE _ GROUP BY _",
"SELECT _ FROM _ WHERE _",
"SELECT _ FROM _ GROUP BY _ ORDER BY _"
```
============================ demonstration 2 ============================
【Database Schema】
【DB_ID】 sales
【Schema】
# Table: Customers
[
(CustomerID:INTEGER, Primary Key, Examples: [1, 2, 3]),
(FirstName:TEXT, Examples: [Aaron, Abby, Abe]),
(MiddleInitial:TEXT, Examples: [A, B, C]),
(LastName:TEXT, Examples: [Alexander, Bryant, Butler])
]
# Table: Employees
[
(EmployeeID:INTEGER, Primary Key, Examples: [1, 2, 3]),
(FirstName:TEXT, Examples: [Abraham, Reginald, Cheryl]),
(MiddleInitial:TEXT, Examples: [e, l, a]),
(LastName:TEXT, Examples: [Bennet, Blotchet-Halls, Carson])
]
# Table: Products
[
(ProductID:INTEGER, Primary Key, Examples: [1, 2, 3]),
(Name:TEXT, Examples: [Adjustable Race, Bearing Ball, BB Ball Bearing]),
(Price:REAL, Examples: [1.6, 0.8, 2.4])
]
# Table: Sales
[
(SalesID:INTEGER, Primary Key, Examples: [1, 2, 3]),
(SalesPersonID:INTEGER, Examples: [17, 5, 8]),
(CustomerID:INTEGER, Examples: [10482, 1964, 12300]),
(ProductID:INTEGER, Examples: [500, 306, 123]),
(Quantity:INTEGER, Examples: [500, 810, 123])
]
【Foreign keys】
Products.ProductID=Sales.ProductID, Customers.CustomerID=Sales.CustomerID, Employees.EmployeeID=Sales.SalesPersonID

【Question】
Among the sales ID ranges from 1 to 200, what is the percentage of the products with a price ranging from 200 to 300?

Based on the question and schema, generate up to {m} diverse Base skeletons that represent plausible high-level structures for the query.
```sql skeleton
"SELECT _ FROM _ WHERE _"
```
============================ demonstration 3 ============================
【Database Schema】
【DB_ID】 human_resources
【Schema】
# Table: employee
[
(ssn:TEXT, Primary Key, Examples: [000-01-0000, 000-02-2222, 109-87-6543]),
(lastname:TEXT, Examples: [Milgrom, Adams, Wood]),
(firstname:TEXT, Examples: [Patricia, Sandy, Emily]),
(hiredate:TEXT, Examples: [10/1/04, 1/15/01, 3/12/97]),
(salary:TEXT, Examples: [US$57,500.00, US$19,500.00, US$69,000.00]),
(gender:TEXT, Examples: [F, M]),
(performance:TEXT, Examples: [Average, Good, Poor]),
(positionID:INTEGER, Examples: [2, 3, 1]),
(locationID:INTEGER, Examples: [2, 1, 5])
]
# Table: location
[
(locationID:INTEGER, Primary Key, Examples: [1, 2, 3]),
(locationcity:TEXT, Examples: [Atlanta, Boston, Chicago]),
(address:TEXT, Examples: [450 Peachtree Rd, 3 Commons Blvd, 500 Loop Highway]),
(state:TEXT, Examples: [GA, MA, IL]),
(zipcode:INTEGER, Examples: [30316, 2190, 60620]),
(officephone:TEXT, Examples: [(404)333-5555, (617)123-4444, (312)444-6666])
]
# Table: position
[
(positionID:INTEGER, Primary Key, Examples: [1, 2, 3]),
(positiontitle:TEXT, Examples: [Account Representative]),
(educationrequired:TEXT, Examples: [4 year degree, 2 year degree, 6 year degree]),
(minsalary:TEXT, Examples: [US$25,000.00, US$50,000.00, US$18,000.00]),
(maxsalary:TEXT, Examples: [US$75,000.00, US$150,000.00, US$25,000.00])
]
【Foreign keys】
employee.positionID=position.positionID, employee.locationID=location.locationID

【Question】
Which employee's job position requires a higher education level, Jose Rodriguez or Sandy Adams?

Based on the question and schema, generate up to {m} diverse Base skeletons that represent plausible high-level structures for the query.
```sql skeleton
"SELECT _ FROM _ WHERE _",
"SELECT _ FROM _ WHERE _ ORDER BY _"
```
=========================================================================

Here are the the database schema and user’s question:
【Database Schema】
{db_schema}

【Question】
{question}

Based on the question and schema, generate up to {m} diverse Base skeletons that represent plausible high-level structures for the query.

Please strictly follow the format below:
```sql skeleton
"skeleton 1",
"skeleton 2"
...
```"""

prompt_expanded_phase = """You are a SQL expert. Your task is to determine if the given SQL skeleton requires further expansion to answer the user's question. If a deeper nested query is needed, expand the skeleton by adding the subquery structure. Otherwise, if no further nesting is necessary, return the skeleton unchanged. Focus ONLY on the nesting structure; do not add any columns, values, or table information.

Here are 3 input-output demonstrations you can refer to:
============================ demonstration 1 ============================
【Database Schema】
【DB_ID】 bike_share_1
【Schema】
# Table: station
[
(id:INTEGER, Primary Key, Examples: [2, 3, 4]),
(name:TEXT, Examples: [San Jose Diridon Caltrain Station]),
(lat:REAL, Examples: [37.329732, 37.330698, 37.333988]),
(long:REAL, Examples: [-121.90178200000001, -121.888979, -121.894902]),
(dock_count:INTEGER, Examples: [27, 15, 11]),
(city:TEXT, Examples: [San Jose, Redwood City, Mountain View]),
(installation_date:TEXT, Examples: [8/6/2013, 8/5/2013, 8/7/2013])
]
# Table: status
[
(station_id:INTEGER, Examples: [2, 3, 4]),
(bikes_available:INTEGER, Examples: [2, 3, 4]),
(docks_available:INTEGER, Examples: [25, 24, 23]),
(time:TEXT, Examples: [2013/08/29 12:06:01, 2013/08/29 12:07:01, 2013/08/29 12:08:01])
]
# Table: trip
[
(id:INTEGER, Primary Key, Examples: [4069, 4073, 4074]),
(duration:INTEGER, Examples: [174, 1067, 1131]),
(start_date:TEXT, Examples: [8/29/2013 9:08, 8/29/2013 9:24, 8/29/2013 9:25]),
(start_station_name:TEXT, Examples: [2nd at South Park]),
(start_station_id:INTEGER, Examples: [64, 66, 22]),
(end_date:TEXT, Examples: [8/29/2013 9:11, 8/29/2013 9:42, 8/29/2013 9:43]),
(end_station_name:TEXT, Examples: [2nd at South Park]),
(end_station_id:INTEGER, Examples: [64, 69, 22]),
(bike_id:INTEGER, Examples: [288, 321, 317]),
(subscription_type:TEXT, Examples: [Subscriber, Customer]),
(zip_code:INTEGER, Examples: [94114, 94703, 94115])
]
# Table: weather
[
(date:TEXT, Examples: [8/29/2013, 8/30/2013, 8/31/2013]),
(max_temperature_f:INTEGER, Examples: [74, 78, 71]),
(mean_temperature_f:INTEGER, Examples: [68, 69, 64]),
(min_temperature_f:INTEGER, Examples: [61, 60, 57]),
(max_dew_point_f:INTEGER, Examples: [61, 57, 60]),
(mean_dew_point_f:INTEGER, Examples: [58, 56, 60]),
(min_dew_point_f:INTEGER, Examples: [56, 54, 53]),
(max_humidity:INTEGER, Examples: [93, 90, 87]),
(mean_humidity:INTEGER, Examples: [75, 70, 68]),
(min_humidity:INTEGER, Examples: [57, 50, 49]),
(max_sea_level_pressure_inches:REAL, Examples: [30.07, 30.05, 30.0]),
(mean_sea_level_pressure_inches:REAL, Examples: [30.02, 30.0, 29.96]),
(min_sea_level_pressure_inches:REAL, Examples: [29.97, 29.93, 29.92]),
(max_visibility_miles:INTEGER, Examples: [10, 9, 8]),
(mean_visibility_miles:INTEGER, Examples: [10, 9, 8]),
(min_visibility_miles:INTEGER, Examples: [10, 7, 6]),
(max_wind_Speed_mph:INTEGER, Examples: [23, 29, 26]),
(mean_wind_speed_mph:INTEGER, Examples: [11, 13, 15]),
(max_gust_speed_mph:INTEGER, Examples: [28, 35, 31]),
(precipitation_inches:TEXT, Examples: [0, 0.23, T]),
(cloud_cover:INTEGER, Examples: [4, 2, 6]),
(events:TEXT, Examples: [Fog, Rain, Fog-Rain]),
(wind_dir_degrees:INTEGER, Examples: [286, 291, 284]),
(zip_code:TEXT, Examples: [94107, 94063, 94301])
]

【Question】
Which trip had the longest duration? State the start and end station.

【Skeleton】
SELECT _ FROM _ WHERE _

Based on the input skeleton, generate up to {m} diverse and plausible expanded skeletons.
```sql skeleton
"SELECT _ FROM _ WHERE _ = (SELECT _ FROM _)",
"SELECT _ FROM _ WHERE _ >= ALL (SELECT _ FROM _)"
```
============================ demonstration 2 ============================
【Database Schema】
【DB_ID】 cs_semester
【Schema】
# Table: RA
[
(student_id:INTEGER, Primary Key, Examples: [2, 5, 6]),
(capability:INTEGER, Examples: [2, 5, 4]),
(prof_id:INTEGER, Primary Key, Examples: [7, 10, 13]),
(salary:TEXT, Examples: [med, high, low])
]
# Table: course
[
(course_id:INTEGER, Primary Key, Examples: [1, 2, 3]),
(name:TEXT, Examples: [Machine Learning Theory]),
(credit:INTEGER, Examples: [3, 2]),
(diff:INTEGER, Examples: [3, 4, 1])
]
# Table: prof
[
(prof_id:INTEGER, Primary Key, Examples: [1, 2, 3]),
(gender:TEXT, Examples: [Male, Female]),
(first_name:TEXT, Examples: [Nathaniel, Zhihua, Ogdon]),
(last_name:TEXT, Examples: [Pigford, Zhou, Zywicki]),
(email:TEXT),
(popularity:INTEGER, Examples: [3, 2]),
(teachingability:INTEGER, Examples: [5, 1, 2]),
(graduate_from:TEXT, Examples: [University of Washington])
]
# Table: registration
[
(course_id:INTEGER, Primary Key, Examples: [1, 2, 3]),
(student_id:INTEGER, Primary Key, Examples: [2, 3, 4]),
(grade:TEXT, Examples: [A, B, C]),
(sat:INTEGER, Examples: [5, 4, 3])
]
# Table: student
[
(student_id:INTEGER, Primary Key, Examples: [1, 2, 3]),
(f_name:TEXT, Examples: [Kerry, Chrysa, Elsy]),
(l_name:TEXT, Examples: [Pryor, Dine-Hart, Shiril]),
(phone_number:TEXT, Examples: [(243) 6836472, (672) 9245255, (521) 7680522]),
(email:TEXT),
(intelligence:INTEGER, Examples: [5, 2, 1]),
(gpa:REAL, Examples: [2.4, 2.7, 3.5]),
(type:TEXT, Examples: [RPG, TPG, UG])
]
【Foreign keys】
RA.student_id=student.student_id, RA.prof_id=prof.prof_id, registration.student_id=student.student_id, course.course_id=registration.course_id

【Question】
Among the students who got a B in the course Machine Learning Theory, how many of them have a gpa of over 3?

【Skeleton】
SELECT _ FROM _ WHERE _ = _ AND _ IN ( SELECT _ FROM _ WHERE _ )

Based on the input skeleton, generate up to {m} diverse and plausible expanded skeletons.
```sql skeleton
"SELECT _ FROM _ WHERE _ = _ AND _ IN ( SELECT _ FROM _ WHERE _ > _ AND _ IN ( SELECT _ FROM _ WHERE _ ) )",
"SELECT _ FROM _ WHERE _ > _ AND _ IN ( SELECT _ FROM _ WHERE _ IN (SELECT _ FROM _ WHERE _ = _) )"
```
============================ demonstration 3 ============================
【Database Schema】
【DB_ID】 talkingdata
【Schema】
# Table: gender_age
[
(device_id:INTEGER, Primary Key, Examples: [-9221086586254644858, -9221079146476055829, -9221066489596332354]),
(gender:TEXT, Examples: [M, F]),
(age:INTEGER, Examples: [29, 31, 38]),
(group:TEXT, Examples: [M29-31, M32-38, F29-32])
]
# Table: gender_age_test
[
(device_id:INTEGER, Primary Key, Examples: [-9223321966609553846, -9223042152723782980, -9222896629442493034])
]
# Table: gender_age_train
[
(device_id:INTEGER, Primary Key, Examples: [-9223067244542181226, -9222956879900151005, -9222754701995937853]),
(gender:TEXT, Examples: [M, F]),
(age:INTEGER, Examples: [24, 36, 29]),
(group:TEXT, Examples: [M23-26, M32-38, M29-31])
]
# Table: label_categories
[
(label_id:INTEGER, Primary Key, Examples: [1, 2, 3]),
(category:TEXT, Examples: [game-game type, game-Game themes, game-Art Style])
]
# Table: phone_brand_device_model2
[
(device_id:INTEGER, Primary Key, Examples: [-9223321966609553846, -9223067244542181226, -9223042152723782980]),
(phone_brand:TEXT, Primary Key, Examples: [小米, vivo, 三星]),
(device_model:TEXT, Primary Key, Examples: [红米note, Y19T, MI 3])
]
【Foreign keys】
app_events.event_id=events.event_id, app_all.app_id=app_events_relevant.app_id, app_events_relevant.event_id=events_relevant.event_id, app_all.app_id=app_labels.app_id, app_labels.label_id=label_categories.label_id, events_relevant.device_id=gender_age.device_id, gender_age.device_id=phone_brand_device_model2.device_id

【Question】
What is the device model of the device used by the oldest user?

【Skeleton】
SELECT _ FROM _ WHERE _ IN ( SELECT _ FROM _ WHERE age = ( SELECT _ FROM _ ) )

Based on the input skeleton, generate up to {m} diverse and plausible expanded skeletons.
```sql skeleton
"SELECT _ FROM _ WHERE _ IN ( SELECT _ FROM _ WHERE age = ( SELECT _ FROM _ ) )"
```

=========================================================================

Here are the the database schema and user’s question:
【Database Schema】
{db_schema}

【Question】
{question}

【Skeleton】
{skeleton}

Based on the input skeleton, generate up to {m} diverse and plausible expanded skeletons.

Please strictly follow the format below:
```sql skeleton
"skeleton 1",
"skeleton 2"
...
```"""

prompt_detailed_phase_placeholder = """You are a SQL expert. Your task is to detail the given SQL skeleton by specifying all required placeholders and their associated operations. Based on the user's question, replace abstract structural placeholders (_) with specific placeholders like [col], [table], [value] and include any necessary aggregators (e.g., avg, sum, max). Do not specify actual table/column names or joining information yet.

Here are 3 input-output demonstrations you can refer to:
============================ demonstration 1 ============================
【Database Schema】
【DB_ID】 authors
【Schema】
# Table: Author
[
(Id:INTEGER, Primary Key, Examples: [9, 14, 15]),
(Name:TEXT, Examples: [Ernest Jordan, K. MORIBE, D. Jakominich]),
(Affiliation:TEXT)
]
# Table: Conference
[
(Id:INTEGER, Primary Key, Examples: [1, 2, 4]),
(ShortName:TEXT, Examples: [IADIS, IADT, ICOMP]),
(FullName:TEXT),
(HomePage:TEXT)
]
# Table: Journal
[
(Id:INTEGER, Primary Key, Examples: [1, 2, 3]),
(ShortName:TEXT, Examples: [ICOM, AEPIA, IBMRD]),
(FullName:TEXT),
(HomePage:TEXT)
]
# Table: Paper
[
(Id:INTEGER, Primary Key, Examples: [1, 2, 3]),
(Title:TEXT),
(Year:INTEGER, Examples: [2009, 2007, 1963]),
(ConferenceId:INTEGER, Examples: [167, 0, 158]),
(JournalId:INTEGER, Examples: [0, 7234, 16867]),
(Keyword:TEXT)
]
# Table: PaperAuthor
[
(PaperId:INTEGER, Examples: [4, 5, 6]),
(AuthorId:INTEGER, Examples: [1456512, 1102257, 1806301]),
(Name:TEXT, Examples: [ADAM G. JONES, Kazuo Iwama, Asgeir Finnseth]),
(Affiliation:TEXT)
]
【Foreign keys】
Journal.Id=Paper.JournalId, Conference.Id=Paper.ConferenceId, Author.Id=PaperAuthor.AuthorId, Paper.Id=PaperAuthor.PaperId

【Question】
Between \"Standford University\" and \"Massachusetts Institute of Technolgy\", which organization had affiliated with more author.?

【Skeleton】
SELECT _ FROM _ WHERE _ IN _ GROUP BY _ ORDER BY _ DESC LIMIT _

Based on the input skeleton, generate up to {m} diverse and valid detailed skeletons.
```sql skeleton
"SELECT [col] FROM [table] WHERE [col] IN ([value], [value]) GROUP BY [col] ORDER BY COUNT([col]) DESC LIMIT [value]"
```
============================ demonstration 2 ============================
【Database Schema】
【DB_ID】 olympics
【Schema】
# Table: city
[
(id:INTEGER, Primary Key, Examples: [1, 2, 3]),
(city_name:TEXT, Examples: [Barcelona, London, Antwerpen])
]
# Table: medal
[
(id:INTEGER, Primary Key, Examples: [1, 2, 3]),
(medal_name:TEXT, Examples: [Gold, Silver, Bronze])
]
# Table: noc_region
[
(id:INTEGER, Primary Key, Examples: [1, 2, 3]),
(noc:TEXT, Examples: [AFG, AHO, ALB]),
(region_name:TEXT, Examples: [Afghanistan, Netherlands Antilles, Albania])
]
# Table: person
[
(id:INTEGER, Primary Key, Examples: [1, 2, 3]),
(full_name:TEXT, Examples: [A Dijiang, A Lamusi, Gunnar Nielsen Aaby]),
(gender:TEXT, Examples: [M, F]),
(height:INTEGER, Examples: [180, 170, 0]),
(weight:INTEGER, Examples: [80, 60, 0])
]
# Table: person_region
[
(person_id:INTEGER, Examples: [1, 2, 3]),
(region_id:INTEGER, Examples: [42, 56, 146])
]
# Table: sport
[
(id:INTEGER, Primary Key, Examples: [1, 2, 3]),
(sport_name:TEXT, Examples: [Aeronautics, Alpine Skiing, Alpinism])
]
【Foreign keys】
games.id=games_city.games_id, city.id=games_city.city_id, games_competitor.person_id=person.id, games.id=games_competitor.games_id, noc_region.id=person_region.region_id, person.id=person_region.person_id, event.sport_id=sport.id, competitor_event.medal_id=medal.id, competitor_event.event_id=event.id, competitor_event.competitor_id=games_competitor.id

【Question】
How many athletes are there in the region where Clara Hughes is from?

【Skeleton】
SELECT _ FROM _ WHERE _ = ( SELECT _ FROM _ WHERE _ = _ )

Based on the input skeleton, generate up to {m} diverse and valid detailed skeletons.
```sql skeleton
"SELECT COUNT([col]) FROM [table] WHERE [col] = ( SELECT [col] FROM [table] WHERE [col] = [value] )"
```
============================ demonstration 3 ============================
【Database Schema】
【DB_ID】 retail_world
【Schema】
# Table: Categories
[
(CategoryID:INTEGER, Primary Key, Examples: [1, 2, 3]),
(CategoryName:TEXT, Examples: [Beverages, Condiments, Confections]),
(Description:TEXT)
]
# Table: Customers
[
(CustomerID:INTEGER, Primary Key, Examples: [1, 2, 3]),
(CustomerName:TEXT, Examples: [Alfreds Futterkiste]),
(ContactName:TEXT, Examples: [Maria Anders, Ana Trujillo, Antonio Moreno]),
(Address:TEXT, Examples: [Obere Str. 57]),
(City:TEXT, Examples: [Berlin, México D.F., London]),
(PostalCode:TEXT, Examples: [12209, 5021, 5023]),
(Country:TEXT, Examples: [Germany, Mexico, UK])
]
# Table: Employees
[
(EmployeeID:INTEGER, Primary Key, Examples: [1, 2, 3]),
(LastName:TEXT, Examples: [Davolio, Fuller, Leverling]),
(FirstName:TEXT, Examples: [Nancy, Andrew, Janet]),
(BirthDate:DATE, Examples: [1968-12-08]),
(Photo:TEXT, Examples: [EmpID1.pic, EmpID2.pic, EmpID3.pic]),
(Notes:TEXT)
]
# Table: OrderDetails
[
(OrderDetailID:INTEGER, Primary Key, Examples: [1, 2, 3]),
(OrderID:INTEGER, Examples: [10248, 10249, 10250]),
(ProductID:INTEGER, Examples: [11, 42, 72]),
(Quantity:INTEGER, Examples: [12, 10, 5])
]
# Table: Orders
[
(OrderID:INTEGER, Primary Key, Examples: [10248, 10249, 10250]),
(CustomerID:INTEGER, Examples: [90, 81, 34]),
(EmployeeID:INTEGER, Examples: [5, 6, 4]),
(OrderDate:DATETIME, Examples: [1996-07-04 00:00:00]),
(ShipperID:INTEGER, Examples: [3, 1, 2])
]
# Table: Products
[
(ProductID:INTEGER, Primary Key, Examples: [1, 2, 3]),
(ProductName:TEXT, Examples: [Chais, Chang, Aniseed Syrup]),
(SupplierID:INTEGER, Examples: [1, 2, 3]),
(CategoryID:INTEGER, Examples: [1, 2, 7]),
(Unit:TEXT, Examples: [10 boxes x 20 bags, 24 - 12 oz bottles, 12 - 550 ml bottles]),
(Price:REAL, Examples: [18.0, 19.0, 10.0])
]
# Table: Shippers
[
(ShipperID:INTEGER, Primary Key, Examples: [1, 2, 3]),
(ShipperName:TEXT, Examples: [Speedy Express, United Package, Federal Shipping]),
(Phone:TEXT, Examples: [(503) 555-9831, (503) 555-3199, (503) 555-9931])
]
# Table: Suppliers
[
(SupplierID:INTEGER, Primary Key, Examples: [1, 2, 3]),
(SupplierName:TEXT, Examples: [Exotic Liquid]),
(ContactName:TEXT, Examples: [Charlotte Cooper, Shelley Burke, Regina Murphy]),
(Address:TEXT, Examples: [49 Gilbert St., P.O. Box 78934, 707 Oxford Rd.]),
(City:TEXT, Examples: [Londona, New Orleans, Ann Arbor]),
(PostalCode:TEXT, Examples: [EC1 4SD, 70117, 48104]),
(Country:TEXT, Examples: [UK, USA, Japan]),
(Phone:TEXT, Examples: [(171) 555-2222, (100) 555-4822, (313) 555-5735])
]
【Foreign keys】
Products.SupplierID=Suppliers.SupplierID, Categories.CategoryID=Products.CategoryID, Orders.ShipperID=Shippers.ShipperID, Customers.CustomerID=Orders.CustomerID, Employees.EmployeeID=Orders.EmployeeID, OrderDetails.ProductID=Products.ProductID, OrderDetails.OrderID=Orders.OrderID

【Question】
Among the employees who handled orders to Brazil, who has the highest salary and calculate the average salary of them.

【Skeleton】
SELECT _ FROM _ WHERE _ = _ GROUP BY _ ORDER BY _ DESC LIMIT _

Based on the input skeleton, generate up to {m} diverse and plausible expanded skeletons.
```sql skeleton
"SELECT [col], [col], AVG([col]) FROM [table] WHERE [col] = [value] GROUP BY [col], [col] ORDER BY SUM([col]) DESC LIMIT [value]"
```
=========================================================================

Here are the the database schema and user’s question:
【Database Schema】
{db_schema}

【Question】
{question}

【Skeleton】
{skeleton}

Based on the input skeleton, generate up to {m} diverse and plausible expanded skeletons.

Please strictly follow the format below:
```sql skeleton
"skeleton 1",
"skeleton 2"
...
```"""

prompt_detailed_phase_join = """You are a SQL expert. Your task is to determine the required table joining structure for the given SQL skeleton. Based on the user's question and the database schema, identify how many tables need to be joined and add the corresponding JOIN [table] ON [col] = [col] clauses. Focus exclusively on the structure and number of joins; do not specify the actual table or column names.

Here are 3 input-output demonstrations you can refer to:
============================ demonstration 1 ============================
【Database Schema】
【DB_ID】 authors
【Schema】
# Table: Author
[
(Id:INTEGER, Primary Key, Examples: [9, 14, 15]),
(Name:TEXT, Examples: [Ernest Jordan, K. MORIBE, D. Jakominich]),
(Affiliation:TEXT)
]
# Table: Conference
[
(Id:INTEGER, Primary Key, Examples: [1, 2, 4]),
(ShortName:TEXT, Examples: [IADIS, IADT, ICOMP]),
(FullName:TEXT),
(HomePage:TEXT)
]
# Table: Journal
[
(Id:INTEGER, Primary Key, Examples: [1, 2, 3]),
(ShortName:TEXT, Examples: [ICOM, AEPIA, IBMRD]),
(FullName:TEXT),
(HomePage:TEXT)
]
# Table: Paper
[
(Id:INTEGER, Primary Key, Examples: [1, 2, 3]),
(Title:TEXT),
(Year:INTEGER, Examples: [2009, 2007, 1963]),
(ConferenceId:INTEGER, Examples: [167, 0, 158]),
(JournalId:INTEGER, Examples: [0, 7234, 16867]),
(Keyword:TEXT)
]
# Table: PaperAuthor
[
(PaperId:INTEGER, Examples: [4, 5, 6]),
(AuthorId:INTEGER, Examples: [1456512, 1102257, 1806301]),
(Name:TEXT, Examples: [ADAM G. JONES, Kazuo Iwama, Asgeir Finnseth]),
(Affiliation:TEXT)
]
【Foreign keys】
Journal.Id=Paper.JournalId, Conference.Id=Paper.ConferenceId, Author.Id=PaperAuthor.AuthorId, Paper.Id=PaperAuthor.PaperId

【Question】
Between \"Standford University\" and \"Massachusetts Institute of Technolgy\", which organization had affiliated with more author.?

【Skeleton】
SELECT [col] FROM [table] WHERE [col] IN ([value], [value]) GROUP BY [col] ORDER BY COUNT([col]) DESC LIMIT [value]

Based on the input skeleton, generate up to {m} diverse and valid detailed skeletons.
```sql skeleton
"SELECT [col] FROM [table] WHERE [col] IN ([value], [value]) GROUP BY [col] ORDER BY COUNT([col]) DESC LIMIT [value]"
```
============================ demonstration 2 ============================
【Database Schema】
【DB_ID】 olympics
【Schema】
# Table: city
[
(id:INTEGER, Primary Key, Examples: [1, 2, 3]),
(city_name:TEXT, Examples: [Barcelona, London, Antwerpen])
]
# Table: competitor_event
[
(event_id:INTEGER, Examples: [1, 2, 3]),
(competitor_id:INTEGER, Examples: [1, 2, 3]),
(medal_id:INTEGER, Examples: [4, 1, 3])
]
# Table: event
[
(id:INTEGER, Primary Key, Examples: [1, 2, 3]),
(sport_id:INTEGER, Examples: [9, 33, 25]),
(event_name:TEXT, Examples: [Basketball Men's Basketball])
]
# Table: games
[
(id:INTEGER, Primary Key, Examples: [1, 2, 3]),
(games_year:INTEGER, Examples: [1992, 2012, 1920]),
(games_name:TEXT, Examples: [1992 Summer, 2012 Summer, 1920 Summer]),
(season:TEXT, Examples: [Summer, Winter])
]
# Table: games_city
[
(games_id:INTEGER, Examples: [1, 2, 3]),
(city_id:INTEGER, Examples: [1, 2, 3])
]
# Table: games_competitor
[
(id:INTEGER, Primary Key, Examples: [1, 2, 3]),
(games_id:INTEGER, Examples: [1, 2, 3]),
(person_id:INTEGER, Examples: [1, 2, 3]),
(age:INTEGER, Examples: [24, 23, 34])
]
# Table: medal
[
(id:INTEGER, Primary Key, Examples: [1, 2, 3]),
(medal_name:TEXT, Examples: [Gold, Silver, Bronze])
]
# Table: noc_region
[
(id:INTEGER, Primary Key, Examples: [1, 2, 3]),
(noc:TEXT, Examples: [AFG, AHO, ALB]),
(region_name:TEXT, Examples: [Afghanistan, Netherlands Antilles, Albania])
]
# Table: person
[
(id:INTEGER, Primary Key, Examples: [1, 2, 3]),
(full_name:TEXT, Examples: [A Dijiang, A Lamusi, Gunnar Nielsen Aaby]),
(gender:TEXT, Examples: [M, F]),
(height:INTEGER, Examples: [180, 170, 0]),
(weight:INTEGER, Examples: [80, 60, 0])
]
# Table: person_region
[
(person_id:INTEGER, Examples: [1, 2, 3]),
(region_id:INTEGER, Examples: [42, 56, 146])
]
# Table: sport
[
(id:INTEGER, Primary Key, Examples: [1, 2, 3]),
(sport_name:TEXT, Examples: [Aeronautics, Alpine Skiing, Alpinism])
]
【Foreign keys】
games.id=games_city.games_id, city.id=games_city.city_id, games_competitor.person_id=person.id, games.id=games_competitor.games_id, noc_region.id=person_region.region_id, person.id=person_region.person_id, event.sport_id=sport.id, competitor_event.medal_id=medal.id, competitor_event.event_id=event.id, competitor_event.competitor_id=games_competitor.id

【Question】
How many athletes are there in the region where Clara Hughes is from?

【Skeleton】
SELECT _ FROM _ WHERE _ = ( SELECT _ FROM _ WHERE _ = _ )

Based on the input skeleton, generate up to {m} diverse and valid detailed skeletons.
```sql skeleton
"SELECT COUNT([col]) FROM [table] WHERE [col] = ( SELECT [col] FROM [table] JOIN [table] ON [col] = [col] WHERE [col] = [value] )"
```
============================ demonstration 3 ============================
【Database Schema】
【DB_ID】 retail_world
【Schema】
# Table: Categories
[
(CategoryID:INTEGER, Primary Key, Examples: [1, 2, 3]),
(CategoryName:TEXT, Examples: [Beverages, Condiments, Confections]),
(Description:TEXT)
]
# Table: Customers
[
(CustomerID:INTEGER, Primary Key, Examples: [1, 2, 3]),
(CustomerName:TEXT, Examples: [Alfreds Futterkiste]),
(ContactName:TEXT, Examples: [Maria Anders, Ana Trujillo, Antonio Moreno]),
(Address:TEXT, Examples: [Obere Str. 57]),
(City:TEXT, Examples: [Berlin, México D.F., London]),
(PostalCode:TEXT, Examples: [12209, 5021, 5023]),
(Country:TEXT, Examples: [Germany, Mexico, UK])
]
# Table: Employees
[
(EmployeeID:INTEGER, Primary Key, Examples: [1, 2, 3]),
(LastName:TEXT, Examples: [Davolio, Fuller, Leverling]),
(FirstName:TEXT, Examples: [Nancy, Andrew, Janet]),
(BirthDate:DATE, Examples: [1968-12-08]),
(Photo:TEXT, Examples: [EmpID1.pic, EmpID2.pic, EmpID3.pic]),
(Notes:TEXT)
]
# Table: OrderDetails
[
(OrderDetailID:INTEGER, Primary Key, Examples: [1, 2, 3]),
(OrderID:INTEGER, Examples: [10248, 10249, 10250]),
(ProductID:INTEGER, Examples: [11, 42, 72]),
(Quantity:INTEGER, Examples: [12, 10, 5])
]
# Table: Orders
[
(OrderID:INTEGER, Primary Key, Examples: [10248, 10249, 10250]),
(CustomerID:INTEGER, Examples: [90, 81, 34]),
(EmployeeID:INTEGER, Examples: [5, 6, 4]),
(OrderDate:DATETIME, Examples: [1996-07-04 00:00:00]),
(ShipperID:INTEGER, Examples: [3, 1, 2])
]
# Table: Products
[
(ProductID:INTEGER, Primary Key, Examples: [1, 2, 3]),
(ProductName:TEXT, Examples: [Chais, Chang, Aniseed Syrup]),
(SupplierID:INTEGER, Examples: [1, 2, 3]),
(CategoryID:INTEGER, Examples: [1, 2, 7]),
(Unit:TEXT, Examples: [10 boxes x 20 bags, 24 - 12 oz bottles, 12 - 550 ml bottles]),
(Price:REAL, Examples: [18.0, 19.0, 10.0])
]
# Table: Shippers
[
(ShipperID:INTEGER, Primary Key, Examples: [1, 2, 3]),
(ShipperName:TEXT, Examples: [Speedy Express, United Package, Federal Shipping]),
(Phone:TEXT, Examples: [(503) 555-9831, (503) 555-3199, (503) 555-9931])
]
# Table: Suppliers
[
(SupplierID:INTEGER, Primary Key, Examples: [1, 2, 3]),
(SupplierName:TEXT, Examples: [Exotic Liquid]),
(ContactName:TEXT, Examples: [Charlotte Cooper, Shelley Burke, Regina Murphy]),
(Address:TEXT, Examples: [49 Gilbert St., P.O. Box 78934, 707 Oxford Rd.]),
(City:TEXT, Examples: [Londona, New Orleans, Ann Arbor]),
(PostalCode:TEXT, Examples: [EC1 4SD, 70117, 48104]),
(Country:TEXT, Examples: [UK, USA, Japan]),
(Phone:TEXT, Examples: [(171) 555-2222, (100) 555-4822, (313) 555-5735])
]
【Foreign keys】
Products.SupplierID=Suppliers.SupplierID, Categories.CategoryID=Products.CategoryID, Orders.ShipperID=Shippers.ShipperID, Customers.CustomerID=Orders.CustomerID, Employees.EmployeeID=Orders.EmployeeID, OrderDetails.ProductID=Products.ProductID, OrderDetails.OrderID=Orders.OrderID

【Question】
Among the employees who handled orders to Brazil, who has the highest salary and calculate the average salary of them.

【Skeleton】
SELECT _ FROM _ WHERE _ = _ GROUP BY _ ORDER BY _ DESC LIMIT _

Based on the input skeleton, generate up to {m} diverse and plausible expanded skeletons.
```sql skeleton
"SELECT [col], [col], AVG([col]) FROM [table] JOIN [table] ON [col] = [col] WHERE [col] = [value] GROUP BY [col], [col] ORDER BY SUM([col]) DESC LIMIT [value]"
```
=========================================================================

Here are the the database schema and user’s question:
【Database Schema】
{db_schema}

【Question】
{question}

【Skeleton】
{skeleton}

Based on the input skeleton, generate up to {m} diverse and plausible expanded skeletons.

Please strictly follow the format below:
```sql skeleton
"skeleton 1",
"skeleton 2"
...
```"""

from openai import OpenAI, AsyncOpenAI
# from src.utils import ast_norma
import re
import asyncio


def model(base_url, api_key, model_name, prompt):
    try:
        client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )
    
        chat_completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant specializing in SQL skeleton generation."},
                {"role": "user", "content": prompt},
            ],
            extra_body={
                "chat_template_kwargs": {"enable_thinking": False},
            },
            temperature=0.8,
            max_tokens=1024,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        print(f"An error occurred in the 'model' function: {e}")
        return "" 


async def model_async(base_url, api_key, model_name, prompt, stats=None, module_name=None):
    try:
        client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
        )
    
        chat_completion = await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant specializing in SQL skeleton generation."},
                {"role": "user", "content": prompt},
            ],
            extra_body={
                "chat_template_kwargs": {"enable_thinking": False},
            },
            temperature=0.8,
            max_tokens=1024,
            timeout=60,
        )
        if stats is not None and module_name is not None and chat_completion.usage:
            stats[module_name] = stats.get(module_name, 0) + chat_completion.usage.total_tokens
        return chat_completion.choices[0].message.content
    except Exception:
        return "" 


def extract_sql_skeletons(text):
    pattern = r'```sql skeleton\s*(.*?)\s*```'
    
    matches = re.findall(pattern, text, re.DOTALL)
    
    if matches:
        content = matches[0]
        skeleton_pattern = r'"([^"]*)"'
        skeletons = re.findall(skeleton_pattern, content)

        cleaned_skeletons = []
        for skeleton in skeletons:
            cleaned = skeleton.rstrip(',').strip()
            cleaned_skeletons.append(cleaned)
        
        return cleaned_skeletons
    
    return []


def skefor_agent(question, db_schema, parent_skeleton, m, phase, base_url, api_key, model_name):
    if phase.lower() == "base":
        prompt = prompt_base_phase.format(db_schema=db_schema, question=question, m=m)

    elif phase.lower() == "expanded":
        prompt = prompt_expanded_phase.format(db_schema=db_schema, question=question, skeleton=parent_skeleton, m=m)

    elif phase.lower() == "detailed_placeholder":
        prompt = prompt_detailed_phase_placeholder.format(db_schema=db_schema, question=question, skeleton=parent_skeleton, m=m)

    elif phase.lower() == "detailed_join": 
        prompt = prompt_detailed_phase_join.format(db_schema=db_schema, question=question, skeleton=parent_skeleton, m=m)
    else:
        return []
    
    model_output = model(base_url, api_key, model_name, prompt)

    skeleton_list = extract_sql_skeletons(model_output)

    # skeleton_list = ast_norma(skeleton_list)

    return skeleton_list


async def skefor_agent_async(question, db_schema, parent_skeleton, m, phase, base_url, api_key, model_name, stats=None):
    if phase == "Base":
        prompt = prompt_base_phase.format(m=m, db_schema=db_schema, question=question)
    elif phase == "Expanded":
        prompt = prompt_expanded_phase.format(m=m, db_schema=db_schema, question=question, skeleton=parent_skeleton)
    elif phase == "detailed_placeholder":
        prompt = prompt_detailed_phase_placeholder.format(m=m, db_schema=db_schema, question=question, skeleton=parent_skeleton)
    elif phase == "detailed_join":
        prompt = prompt_detailed_phase_join.format(m=m, db_schema=db_schema, question=question, skeleton=parent_skeleton)
    else:
        return []

    model_output = await model_async(base_url, api_key, model_name, prompt, stats, 'skefor')
    skeletons = extract_sql_skeletons(model_output)
    
    return skeletons
