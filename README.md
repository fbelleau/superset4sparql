# Superset4SPARQL

A REST API to query SPARQL endpoints using Apache Superset BI tool using the elasticsearc-dbapi package.

## Context

Bio2RDF project was beneficial to the life science community because it provided a common data integration framework that allowed researchers to easily combine and analyze data from different sources. Since then, many life science data providers have adopted the RDF publication approach but, after more than 15 years, we can not say that semantic web technology was widely adopted by bioinformaticians.

The lack of data visualization tools can hinder the development and usability of semantic web applications by making it difficult to understand and work with complex data structures and relationships. Since the Facet browser of Virtuoso, a web tool that explores RDF triplestore by facet browsing, very few frameworks have eased the building of a dashboard. Although commercial software, such as Ontotext and Stardog, are offering dashboard tools, they cannot match the simplicity and popularity of Tableau and PowerBI.

A mature business intelligence (BI) software tool capable of building a dashboard from SPARQL endpoints could provide significant benefits to the life science community by enabling efficient data analysis, integrating data sources, designing data visualization, and promoting collaboration and sharing.

## Goal

The goal of this project is to modify an existing business intelligence (BI) tool to enable it to consume SPARQL endpoints. During the biohackathon, we aim to build BI  tool that will make it possible to build a dashboard from RDF resources in the fields of multi-omics analysis, genomics, transcriptomics, epigenomics, proteomics, protein structures, and biochemical data.

For this project, we have selected Superset as the dashboard technology. Superset is an open-source Apache BI software that is compatible with many cloud-based SQL technologies. One such technology is Elasticsearch, for which a Python package (https://pypi.org/project/elasticsearch-dbapi/) has made it possible to enable communication between Superset and Elasticsearch using the existing SQL REST API.

## Method

Our strategy is to first create a REST API that mimics Elasticsearch behavior using a QLever SPARQL endpoint containing Uniprot data (https://qlever.cs.uni-freiburg.de/uniprot). Superset, an open source Apache BI software tool compatible with various cloud-based SQL technologies, uses SQLAlchemy (https://www.sqlalchemy.org/) to generate SQL queries submitted to cloud datasource APIs. Our main task will be to translate SQL statements generated by Superset's dashboard building interface into their SPARQL equivalent queries, which we will submit to the QLever SPARQL endpoint. An example of SQL to SPARQL conversion can be found in the project's GitHub repository, where ChatGPT has already performed the translation. In this project, we aim to create a SQL2SPARQL package using Python to perform the same translation. SQL and SPARQL query parsers already exist, so we only need to build the necessary translator. 

Once the project is successful, we will create a sparql-dbapi Python package to enable Superset/SPARQL connectivity. This will allow us to build dashboards for Life Science users using existing SPARQL resources, and promote further adoption of the RDF data model in the Life Science field.

## Invitation to participates

If you would like to participate to this project open an issue with your comments and I will contact you.

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

# SPARQL in Superset, what it could be ! 

<img width="1429" alt="image" src="https://user-images.githubusercontent.com/995409/229241652-25eb6370-5b3d-4b4c-936f-20df35f0323f.png">

<img width="1429" alt="image" src="https://user-images.githubusercontent.com/995409/229241804-d62df880-766a-4070-9c87-ee2c83ca2fc6.png">


````
