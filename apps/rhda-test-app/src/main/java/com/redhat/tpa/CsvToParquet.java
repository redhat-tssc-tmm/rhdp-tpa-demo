package com.redhat.tpa;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Files;
import java.nio.file.Path;

import org.apache.avro.Schema;
import org.apache.avro.generic.GenericData;
import org.apache.avro.generic.GenericRecord;
import org.apache.hadoop.conf.Configuration;
import org.apache.parquet.avro.AvroParquetWriter;
import org.apache.parquet.hadoop.ParquetWriter;
import org.apache.parquet.hadoop.metadata.CompressionCodecName;

/**
 * Converts a CSV of software components into Apache Parquet format.
 *
 * This app uses parquet-avro 1.11.0, which has known critical vulnerabilities
 * (CVE-2025-30065, CVE-2025-46762) that the RHDA plugin should detect.
 *
 * Usage: java -jar rhda-test-app.jar [output.parquet]
 */
public class CsvToParquet {

    private static final String SCHEMA_JSON = """
            {
              "type": "record",
              "name": "SoftwareComponent",
              "namespace": "com.redhat.tpa",
              "fields": [
                {"name": "name",      "type": "string"},
                {"name": "version",   "type": "string"},
                {"name": "ecosystem", "type": "string"},
                {"name": "purl",      "type": "string"}
              ]
            }
            """;

    private static final String[][] SAMPLE_DATA = {
        {"log4j-core",       "2.14.1",  "maven", "pkg:maven/org.apache.logging.log4j/log4j-core@2.14.1"},
        {"jackson-databind", "2.13.1",  "maven", "pkg:maven/com.fasterxml.jackson.core/jackson-databind@2.13.1"},
        {"parquet-avro",     "1.11.0",  "maven", "pkg:maven/org.apache.parquet/parquet-avro@1.11.0"},
        {"spring-core",      "5.3.18",  "maven", "pkg:maven/org.springframework/spring-core@5.3.18"},
        {"guava",            "31.0.1",  "maven", "pkg:maven/com.google.guava/guava@31.0.1-jre"},
    };

    public static void main(String[] args) throws IOException {
        String outputFile = args.length > 0 ? args[0] : "components.parquet";
        Path outputPath = Path.of(outputFile);

        System.out.println("CSV to Parquet Converter");
        System.out.println("========================");
        System.out.printf("Writing %d software components to %s%n", SAMPLE_DATA.length, outputFile);

        Schema schema = new Schema.Parser().parse(SCHEMA_JSON);
        org.apache.hadoop.fs.Path hadoopPath = new org.apache.hadoop.fs.Path(outputPath.toAbsolutePath().toString());

        try (ParquetWriter<GenericRecord> writer = AvroParquetWriter.<GenericRecord>builder(hadoopPath)
                .withSchema(schema)
                .withCompressionCodec(CompressionCodecName.SNAPPY)
                .withConf(new Configuration())
                .build()) {

            for (String[] row : SAMPLE_DATA) {
                GenericRecord record = new GenericData.Record(schema);
                record.put("name", row[0]);
                record.put("version", row[1]);
                record.put("ecosystem", row[2]);
                record.put("purl", row[3]);
                writer.write(record);
                System.out.printf("  + %s@%s (%s)%n", row[0], row[1], row[2]);
            }
        }

        long fileSize = Files.size(outputPath);
        System.out.printf("%nDone. Wrote %s (%d bytes)%n", outputFile, fileSize);
    }
}
