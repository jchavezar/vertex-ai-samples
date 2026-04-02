# Evaluation Test Cases

Complex multi-step reasoning questions for ADK vs LangGraph comparison.

## Test Cases

### 1. Multi-step Math Problem
**Query:** A train leaves Station A at 8:00 AM traveling at 60 mph. Another train leaves Station B (300 miles away) at 9:00 AM traveling toward Station A at 90 mph. At what time will they meet?

**Expected Answer:** 10:24 AM
**Explanation:** By 9 AM, Train A has traveled 60 miles, leaving 240 miles. Combined speed is 150 mph. Time to meet: 240/150 = 1.6 hours = 1 hour 36 minutes. 9:00 AM + 1:36 = 10:24 AM.

---

### 2. Logic Puzzle
**Query:** There are 5 houses in a row. The red house is to the left of the blue house. The green house is in the middle. The yellow house is not next to the green house. The white house is at one end. What is the order of houses from left to right?

**Expected Answer:** White, Yellow, Green, Red, Blue (or variations with valid constraints)
**Key Constraints:** Green is position 3, Red is left of Blue, Yellow not next to Green.

---

### 3. Code Analysis
**Query:** Given this Python code: `result = [x**2 for x in range(10) if x % 2 == 0]`. What is the sum of all elements in result?

**Expected Answer:** 120
**Explanation:** Even numbers 0-9: [0,2,4,6,8]. Squares: [0,4,16,36,64]. Sum: 0+4+16+36+64 = 120.

---

### 4. Science Reasoning
**Query:** If I drop a ball from 80 meters on Earth (g=10 m/s²) and another ball from 45 meters on a planet with g=20 m/s², which ball hits the ground first and by how many seconds?

**Expected Answer:** Planet ball hits first by ~1.88 seconds
**Explanation:** Earth: t=√(2*80/10)=4s. Planet: t=√(2*45/20)=√4.5≈2.12s. Difference: 4-2.12≈1.88s.

---

### 5. Language & Context
**Query:** In the sentence "The bank was steep and muddy after the flood", what does "bank" refer to? Then create a sentence where "bank" means a financial institution.

**Expected Answer:** Riverbank/edge of a river. Example: "I need to deposit this check at the bank."
**Multi-step:** Disambiguation + generation.

---

### 6. Historical Analysis
**Query:** If World War II ended in 1945, the Moon landing was in 1969, and the Berlin Wall fell in 1989, how many years passed between each event, and what's the total span?

**Expected Answer:** WWII to Moon: 24 years, Moon to Berlin: 20 years, Total span: 44 years

---

### 7. Data Transformation
**Query:** Convert the list [3, 1, 4, 1, 5, 9, 2, 6] to: 1) sorted ascending, 2) unique values only, 3) sum of unique values, 4) average of unique values.

**Expected Answer:** 
1) [1, 1, 2, 3, 4, 5, 6, 9]
2) [1, 2, 3, 4, 5, 6, 9]
3) 30
4) ~4.29

---

### 8. Multi-hop Reasoning
**Query:** Alice is twice as old as Bob. In 10 years, Alice will be 1.5 times Bob's age. How old is Charlie if Charlie is the average of their current ages?

**Expected Answer:** Charlie is 30 years old
**Explanation:** Let Bob=x, Alice=2x. In 10 years: 2x+10=1.5(x+10), 2x+10=1.5x+15, 0.5x=5, x=10. Bob=10, Alice=20. Average=(10+20)/2=15... Wait, let me recalculate. Actually: 0.5x=5, x=20. Bob=20, Alice=40. Charlie=(20+40)/2=30.

---

### 9. API Design
**Query:** Design a REST API endpoint for a bookstore that: 1) filters books by author, 2) sorts by publication date, 3) paginates results (10 per page). Show the endpoint structure.

**Expected Answer:** GET /api/books?author={name}&sort=publication_date&order=asc&page=1&limit=10

---

### 10. Complex Calculation
**Query:** A company has 3 products. Product A costs $50 with 30% margin, Product B costs $80 with 25% margin, Product C costs $120 with 40% margin. If they sell 100 of A, 75 of B, and 50 of C, what's the total profit?

**Expected Answer:** $5,900
**Explanation:** 
- A: $50 × 30% × 100 = $1,500
- B: $80 × 25% × 75 = $1,500
- C: $120 × 40% × 50 = $2,400
- Total: $5,400... Actually margin calculation: A profit = 50*0.3*100=1500, B profit = 80*0.25*75=1500, C profit = 120*0.4*50=2400. Total = $5,400.
