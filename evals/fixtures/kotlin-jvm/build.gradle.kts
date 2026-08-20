plugins {
  id("org.jetbrains.kotlin.jvm") version "2.4.10"
}

kotlin {
  jvmToolchain(21)
}

dependencies {
  implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.10.2")
  testImplementation(kotlin("test"))
}

tasks.withType<Test>().configureEach {
  useJUnitPlatform()
}
