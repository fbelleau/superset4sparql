# superset4sparql
A REST API to query SPARQL endpoint using Apache Superset BI tool

## Example of a SQL query converted to SPARQL done by ChatGPT

````
SELECT enzyme.enzyme_name, COUNT(DISTINCT reaction_protein.protein) AS count, publication.publication_title
FROM reaction_enzyme
JOIN enzyme ON reaction_enzyme.enzyme = enzyme.enzyme_uri
JOIN reaction_protein ON reaction_enzyme.reaction = reaction_protein.reaction
JOIN publication ON publication.publication_uri IN (
  SELECT DISTINCT publication.publication_uri
  FROM enzyme
  JOIN publication ON publication.publication_uri IN (
    SELECT DISTINCT mentions.publication_uri
    FROM mentions
    WHERE mentions.enzyme_uri = enzyme.enzyme_uri
  )
)
GROUP BY enzyme.enzyme_name, publication.publication_title
ORDER BY count DESC
````

converted to

````
PREFIX bio2rdf: <http://bio2rdf.org/>

SELECT ?enzyme (COUNT(DISTINCT ?protein) AS ?count) ?title
WHERE {
  ?reaction a bio2rdf:Reaction .
  ?reaction bio2rdf:reaction_enzyme ?enzyme .
  ?reaction bio2rdf:reaction_protein ?protein .
  
  {
    SELECT ?enzyme ?title
    WHERE {
      ?enzyme a bio2rdf:Enzyme .
      ?enzyme bio2rdf:enzyme_name ?name .
      ?publication a bio2rdf:Publication .
      ?publication bio2rdf:mentions ?enzyme .
      ?publication bio2rdf:publication_title ?title .
    }
  }
}
GROUP BY ?enzyme ?title
ORDER BY DESC(?count)
````
