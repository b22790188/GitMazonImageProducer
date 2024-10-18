FROM maven:3.8.5 AS builder

WORKDIR /app

COPY pom.xml .

COPY src ./src

RUN mvn clean package


FROM eclipse-temurin:17.0.12_7-jre-jammy

WORKDIR /app

EXPOSE 8080

RUN apt-get update && apt-get install -y vim

COPY --from=builder /app/src/main/resources/application.properties .

COPY --from=builder /app/target/*.jar ./app.jar

CMD ["java", "-jar", "app.jar"]
