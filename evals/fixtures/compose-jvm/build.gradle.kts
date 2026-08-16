plugins {
  id("org.jetbrains.kotlin.jvm") version "2.4.10"
  id("org.jetbrains.kotlin.plugin.compose") version "2.4.10"
  id("org.jetbrains.compose") version "1.11.1"
}

kotlin {
  jvmToolchain(21)
}

dependencies {
  implementation(compose.desktop.currentOs)
  implementation("org.jetbrains.kotlinx:kotlinx-collections-immutable:0.5.1")
  testImplementation(kotlin("test"))
  testImplementation("org.jetbrains.compose.ui:ui-test-junit4:1.11.1")
}

tasks.withType<Test>().configureEach {
  useJUnitPlatform()
}
