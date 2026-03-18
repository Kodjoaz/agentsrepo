using SampleLibrary;

namespace SampleLibraryTests;

public class GreeterTests
{
    [Fact]
    public void SayHello_ReturnsGreetingForProvidedName()
    {
        var result = Greeter.SayHello("Alice");

        Assert.Equal("Hello, Alice!", result);
    }

    [Theory]
    [InlineData("")]
    [InlineData(" ")]
    [InlineData("   ")]
    public void SayHello_UsesWorldFallbackForBlankInput(string name)
    {
        var result = Greeter.SayHello(name);

        Assert.Equal("Hello, World!", result);
    }

    [Fact]
    public void SayHello_UsesWorldFallbackForNullInput()
    {
        var result = Greeter.SayHello(null);

        Assert.Equal("Hello, World!", result);
    }
}