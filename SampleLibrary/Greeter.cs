namespace SampleLibrary;

public static class Greeter
{
    public static string SayHello(string? name)
    {
        if (string.IsNullOrWhiteSpace(name))
        {
            name = "World";
        }

        return $"Hello, {name}!";
    }
}