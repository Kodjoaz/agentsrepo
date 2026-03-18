# agentsrepo

Sample .NET 8 solution with:

- `SampleLibrary`: a class library that exposes a simple greeting API
- `SampleConsole`: a console app that references the library and prints a greeting
- `SampleLibrary.Tests`: an xUnit test project that verifies the library behavior

## Prerequisites

- .NET 8 SDK

## Solution layout

```text
AgentsRepo.sln
SampleLibrary/
SampleConsole/
SampleLibrary.Tests/
```

## Projects

- `SampleConsole`: entry point in `SampleConsole/Program.cs`
- `SampleLibrary`: greeting implementation in `SampleLibrary/Greeter.cs`
- `SampleLibrary.Tests`: unit tests in `SampleLibrary.Tests/UnitTest1.cs`

## Build

```powershell
dotnet build .\AgentsRepo.sln
```

## Run

Run with the default name:

```powershell
dotnet run --project .\SampleConsole
```

Expected default output:

```text
Hello, Developer!
```

Run with a custom name:

```powershell
dotnet run --project .\SampleConsole -- Alice
```

Expected output:

```text
Hello, Alice!
```

## Test

```powershell
dotnet test .\AgentsRepo.sln
```

## Coverage

Collect code coverage for the test project:

```powershell
dotnet test .\SampleLibrary.Tests\SampleLibrary.Tests.csproj --collect:"XPlat Code Coverage"
```

Coverage results are written under:

```text
SampleLibrary.Tests/TestResults/
```

The generated report format is Cobertura XML.

## Implementation notes

- `SampleConsole` reads the first command-line argument.
- If no argument is provided, it falls back to `Developer`.
- `SampleLibrary.Greeter.SayHello` is implemented in `SampleLibrary/Greeter.cs`.
- `SampleLibrary.Greeter.SayHello` accepts nullable input and falls back to `World` for null, empty, or whitespace values.
- `SampleLibrary.Tests` covers direct-name input plus null and blank fallback behavior.