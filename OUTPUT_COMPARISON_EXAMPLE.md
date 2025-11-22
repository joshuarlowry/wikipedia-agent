# Output Format Comparison

This document shows the difference between MLA and JSON modes using the same query.

## Query
**"What is quantum computing?"**

---

## MLA Mode Output (Default)

```
Quantum computing is a revolutionary approach to computation that leverages 
quantum mechanical phenomena such as superposition and entanglement to process 
information ("Quantum Computing"). Unlike classical computers that use bits 
representing either 0 or 1, quantum computers use quantum bits, or qubits, 
which can exist in multiple states simultaneously due to superposition 
("Qubit"). This property allows quantum computers to perform certain 
calculations exponentially faster than classical computers.

A qubit is the basic unit of quantum information, analogous to the classical 
bit ("Qubit"). However, while a classical bit can only be in one of two 
states (0 or 1), a qubit can exist in a superposition of both states 
simultaneously. When measured, the qubit collapses to either 0 or 1, but 
before measurement, it contains both possibilities. This fundamental difference 
enables quantum computers to explore multiple solutions to a problem at once.

Quantum algorithms are designed to take advantage of quantum mechanical 
properties to solve specific problems more efficiently than classical 
algorithms ("Quantum Algorithm"). Notable examples include Shor's algorithm 
for factoring large numbers and Grover's algorithm for searching unsorted 
databases. These algorithms demonstrate the potential of quantum computing 
to revolutionize fields such as cryptography, drug discovery, and optimization 
problems.

Works Cited
"Quantum Computing." Wikipedia, Wikimedia Foundation, 15 Nov. 2024, 
    en.wikipedia.org/wiki/Quantum_computing. Accessed 22 Nov. 2025.
"Qubit." Wikipedia, Wikimedia Foundation, 10 Nov. 2024, 
    en.wikipedia.org/wiki/Qubit. Accessed 22 Nov. 2025.
"Quantum Algorithm." Wikipedia, Wikimedia Foundation, 8 Nov. 2024, 
    en.wikipedia.org/wiki/Quantum_algorithm. Accessed 22 Nov. 2025.
```

**Characteristics:**
- ✓ Natural narrative flow
- ✓ Human-readable prose
- ✓ In-text citations with article titles
- ✓ Formal Works Cited section
- ✓ Good for academic papers, reports, articles

---

## JSON Mode Output

```json
{
  "query": "What is quantum computing?",
  "sources": [
    {
      "id": "source_1",
      "title": "Quantum computing",
      "url": "https://en.wikipedia.org/wiki/Quantum_computing",
      "last_modified": "2024-11-15",
      "word_count": 5234
    },
    {
      "id": "source_2",
      "title": "Qubit",
      "url": "https://en.wikipedia.org/wiki/Qubit",
      "last_modified": "2024-11-10",
      "word_count": 3892
    },
    {
      "id": "source_3",
      "title": "Quantum algorithm",
      "url": "https://en.wikipedia.org/wiki/Quantum_algorithm",
      "last_modified": "2024-11-08",
      "word_count": 2156
    }
  ],
  "facts": [
    {
      "fact": "Quantum computing uses quantum mechanical phenomena such as superposition and entanglement to process information",
      "source_ids": ["source_1"],
      "category": "definition"
    },
    {
      "fact": "Classical computers use bits that represent either 0 or 1, while quantum computers use qubits",
      "source_ids": ["source_1", "source_2"],
      "category": "technical"
    },
    {
      "fact": "Qubits can exist in multiple states simultaneously due to superposition",
      "source_ids": ["source_2"],
      "category": "technical"
    },
    {
      "fact": "Quantum computers can perform certain calculations exponentially faster than classical computers",
      "source_ids": ["source_1", "source_3"],
      "category": "application"
    },
    {
      "fact": "A qubit is the basic unit of quantum information, analogous to the classical bit",
      "source_ids": ["source_2"],
      "category": "definition"
    },
    {
      "fact": "When measured, a qubit collapses to either 0 or 1, but before measurement contains both possibilities",
      "source_ids": ["source_2"],
      "category": "technical"
    },
    {
      "fact": "Quantum algorithms are designed to take advantage of quantum mechanical properties to solve problems more efficiently",
      "source_ids": ["source_3"],
      "category": "definition"
    },
    {
      "fact": "Shor's algorithm is used for factoring large numbers",
      "source_ids": ["source_3"],
      "category": "application"
    },
    {
      "fact": "Grover's algorithm is used for searching unsorted databases",
      "source_ids": ["source_3"],
      "category": "application"
    },
    {
      "fact": "Quantum computing has potential applications in cryptography, drug discovery, and optimization problems",
      "source_ids": ["source_1", "source_3"],
      "category": "application"
    }
  ],
  "summary": "Quantum computing leverages quantum mechanical phenomena like superposition and entanglement to process information using qubits instead of classical bits. This enables quantum computers to solve certain problems exponentially faster than classical computers, with applications in cryptography, drug discovery, and optimization."
}
```

**Characteristics:**
- ✓ Structured, machine-readable format
- ✓ Explicit source metadata
- ✓ Atomic facts with references
- ✓ Fact categorization
- ✓ Easy to parse and integrate
- ✓ Good for APIs, data pipelines, knowledge bases

---

## Use Case Comparison

| Scenario | Best Mode | Reason |
|----------|-----------|--------|
| Academic paper | MLA | Need proper citations and narrative flow |
| Blog post | MLA | Human-readable, engaging content |
| API endpoint | JSON | Structured, programmatic access |
| Knowledge base | JSON | Easy to index and search facts |
| Data pipeline | JSON | Machine-readable, consistent structure |
| Fact extraction | JSON | Explicit source references |
| Research report | MLA | Professional formatting with citations |
| Chatbot training | JSON | Structured facts for learning |
| Database import | JSON | Easy to parse and store |
| Student essay | MLA | Proper academic citation format |

---

## Integration Examples

### MLA Mode - Display on Website
```python
response = agent.query("What is quantum computing?")
# Direct display - already formatted for reading
return render_template('article.html', content=response)
```

### JSON Mode - Build Knowledge Graph
```python
import json
response = agent.query("What is quantum computing?")
data = json.loads(response)

# Create nodes for sources
for source in data['sources']:
    db.create_node('Source', source)

# Create nodes for facts with relationships
for fact in data['facts']:
    fact_node = db.create_node('Fact', {
        'text': fact['fact'],
        'category': fact['category']
    })
    # Link to sources
    for source_id in fact['source_ids']:
        db.create_relationship(fact_node, source_id, 'SOURCED_FROM')
```

### JSON Mode - Feed to ML Model
```python
import json
response = agent.query("What is quantum computing?")
data = json.loads(response)

# Extract facts for training data
training_examples = []
for fact in data['facts']:
    training_examples.append({
        'text': fact['fact'],
        'label': fact['category'],
        'sources': fact['source_ids']
    })

model.train(training_examples)
```

---

## Summary

**MLA Mode**: Perfect for human consumption, academic work, and content creation  
**JSON Mode**: Perfect for automation, integration, and data processing

Both modes provide accurate, source-backed information from Wikipedia, just in different formats optimized for different use cases.
